from django.conf import settings
from django.core.mail import send_mass_mail
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdminRole, IsTeacherRole
from .class_serializers import (
    AttendanceStatusUpdateSerializer,
    ClassSessionAttendanceSerializer,
    ClassSessionCommentSerializer,
    ClassSessionCommentWriteSerializer,
    ClassSessionHomeworkSerializer,
    ClassSessionMaterialSerializer,
    ClassSessionSerializer,
    ClassSessionWriteSerializer,
    HomeworkFeedbackSerializer,
    HomeworkSubmittedUpdateSerializer,
    TeachingClassDetailSerializer,
    TeachingClassListSerializer,
    TeachingClassTeacherUpdateSerializer,
)
from .models import (
    ClassMembership,
    ClassSession,
    ClassSessionAttendance,
    ClassSessionComment,
    ClassSessionHomework,
    ClassSessionMaterial,
    SchoolSettings,
    Student,
    TeachingClass,
)
from .storage import apply_storage_metadata, delete_stored_file, homework_storage_backend_name
from .tenancy import resolve_school

ALLOWED_HOMEWORK_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/gif',
    'application/pdf',
    'audio/mpeg',
    'audio/mp4',
    'audio/wav',
    'audio/x-wav',
    'audio/webm',
    'audio/ogg',
}
ALLOWED_MATERIAL_TYPES = ALLOWED_HOMEWORK_TYPES | {
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
}
MAX_HOMEWORK_BYTES = 10 * 1024 * 1024
MAX_MATERIAL_BYTES = 20 * 1024 * 1024


def _school(user):
    return resolve_school(required=True)


def _teacher_profile(user):
    return getattr(user, 'teacher_profile', None)


def _student_profile(user):
    return getattr(user, 'student_profile', None)


def _is_admin(user):
    return user.role == user.Roles.ADMIN or user.is_superuser


def _is_teacher(user):
    return user.role == user.Roles.TEACHER


def _is_student(user):
    return user.role == user.Roles.STUDENT


def _classes_for_user(user):
    qs = TeachingClass.objects.filter(is_active=True)
    if _is_admin(user):
        return qs
    if _is_teacher(user):
        teacher = _teacher_profile(user)
        if not teacher:
            return qs.none()
        return qs.filter(Q(teacher_1=teacher) | Q(teacher_2=teacher))
    if _is_student(user):
        student = _student_profile(user)
        if not student or student.account_blocked:
            return qs.none()
        return qs.filter(memberships__student=student).distinct()
    return qs.none()


def _user_can_manage_class(user, teaching_class):
    if _is_admin(user):
        return True
    if _is_teacher(user):
        teacher = _teacher_profile(user)
        return bool(
            teacher
            and (
                teaching_class.teacher_1_id == teacher.id
                or teaching_class.teacher_2_id == teacher.id
            )
        )
    return False


def _user_can_view_class(user, teaching_class):
    if _user_can_manage_class(user, teaching_class):
        return True
    if _is_student(user):
        student = _student_profile(user)
        return bool(
            student
            and not student.account_blocked
            and teaching_class.memberships.filter(student=student).exists()
        )
    return False


def _annotated_classes(qs):
    return qs.select_related(
        'teacher_1__user',
        'teacher_2__user',
    ).annotate(
        _student_count=Count('memberships', distinct=True),
        _session_count=Count('sessions', distinct=True),
    )


class TeachingClassListCreateView(APIView):
    """GET list (role-scoped). POST create (admin only)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = _annotated_classes(_classes_for_user(request.user)).order_by('name')
        return Response(TeachingClassListSerializer(qs, many=True).data)

    def post(self, request):
        if not _is_admin(request.user):
            return Response({'detail': 'Only admins can create classes.'}, status=403)
        serializer = TeachingClassDetailSerializer(
            data=request.data,
            context={'request': request, 'school': _school(request.user)},
        )
        serializer.is_valid(raise_exception=True)
        teaching_class = serializer.save()
        return Response(
            TeachingClassDetailSerializer(
                teaching_class,
                context={'request': request, 'school': _school(request.user)},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class TeachingClassDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get(self, request, pk):
        try:
            return TeachingClass.objects.select_related(
                'teacher_1__user',
                'teacher_2__user',
            ).prefetch_related(
                Prefetch(
                    'memberships',
                    queryset=ClassMembership.objects.select_related('student__user'),
                ),
                Prefetch(
                    'sessions',
                    queryset=ClassSession.objects.order_by('session_date', 'id').prefetch_related(
                        'attendance_records',
                    ),
                ),
                'students__user',
            ).get(pk=pk)
        except TeachingClass.DoesNotExist:
            return None

    def get(self, request, pk):
        teaching_class = self._get(request, pk)
        if not teaching_class or not _user_can_view_class(request.user, teaching_class):
            return Response({'detail': 'Not found.'}, status=404)

        data = TeachingClassDetailSerializer(
            teaching_class,
            context={'request': request, 'school': _school(request.user)},
        ).data

        # Students must not see other students' details/list
        if _is_student(request.user):
            data.pop('students', None)
            data['students'] = []
        return Response(data)

    def patch(self, request, pk):
        teaching_class = self._get(request, pk)
        if not teaching_class:
            return Response({'detail': 'Not found.'}, status=404)

        if _is_admin(request.user):
            serializer = TeachingClassDetailSerializer(
                teaching_class,
                data=request.data,
                partial=True,
                context={'request': request, 'school': _school(request.user)},
            )
            serializer.is_valid(raise_exception=True)
            teaching_class = serializer.save()
            return Response(
                TeachingClassDetailSerializer(
                    teaching_class,
                    context={'request': request, 'school': _school(request.user)},
                ).data
            )

        if _is_teacher(request.user) and _user_can_manage_class(request.user, teaching_class):
            serializer = TeachingClassTeacherUpdateSerializer(
                teaching_class,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            teaching_class = serializer.save(updated_by=request.user)
            return Response(
                TeachingClassDetailSerializer(
                    teaching_class,
                    context={'request': request, 'school': _school(request.user)},
                ).data
            )

        return Response({'detail': 'Not allowed.'}, status=403)

    def delete(self, request, pk):
        if not _is_admin(request.user):
            return Response({'detail': 'Only admins can delete classes.'}, status=403)
        teaching_class = self._get(request, pk)
        if not teaching_class:
            return Response({'detail': 'Not found.'}, status=404)
        teaching_class.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeachingClassStudentBlockView(APIView):
    permission_classes = [IsTeacherRole]

    def post(self, request, pk, student_id):
        try:
            teaching_class = TeachingClass.objects.get(pk=pk)
            student = Student.objects.select_related('user').get(pk=student_id)
        except (TeachingClass.DoesNotExist, Student.DoesNotExist):
            return Response({'detail': 'Not found.'}, status=404)

        if not _user_can_manage_class(request.user, teaching_class):
            return Response({'detail': 'Not allowed.'}, status=403)
        if not teaching_class.memberships.filter(student=student).exists():
            return Response({'detail': 'Student is not enrolled in this class.'}, status=400)
        if student.account_blocked:
            return Response({'detail': 'Student account is already blocked.'}, status=400)

        school_settings = SchoolSettings.objects.order_by('id').first()
        block_threshold = (
            school_settings.unauthorised_absence_block_threshold
            if school_settings
            else 3
        )
        sessions = list(
            ClassSession.objects.filter(
                teaching_class=teaching_class,
                is_started=True,
                session_date__lte=timezone.localdate(),
            ).order_by('-session_date', '-id')[:block_threshold]
        )
        records = {
            record.session_id: record.status
            for record in ClassSessionAttendance.objects.filter(
                session__in=sessions,
                student=student,
            )
        }
        if len(sessions) < block_threshold or any(
            records.get(session.id) != ClassSessionAttendance.Status.UNAUTHORISED_ABSENT
            for session in sessions
        ):
            return Response(
                {
                    'detail': (
                        'Student must be unauthorised absent for the last '
                        f'{block_threshold} started classes.'
                    ),
                },
                status=400,
            )

        reason = str(request.data.get('reason') or '').strip()
        student.account_blocked = True
        student.block_reason = reason or 'absent for the last 3 consecutive classes.'
        student.updated_by = request.user
        student.save(update_fields=['account_blocked', 'block_reason', 'updated_by', 'updated_at'])
        return Response({
            'student_id': student.id,
            'account_blocked': student.account_blocked,
            'block_reason': student.block_reason,
        })


class TeachingClassStudentsView(APIView):
    """Admin add students: POST {student_ids: [1,2]}."""

    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            teaching_class = TeachingClass.objects.get(pk=pk)
        except TeachingClass.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        ids = request.data.get('student_ids') or []
        if not isinstance(ids, list):
            return Response({'student_ids': 'Expected a list of ids.'}, status=400)

        students = Student.objects.filter(pk__in=ids)
        added = []
        for student in students:
            membership, created = ClassMembership.objects.get_or_create(
                teaching_class=teaching_class,
                student=student,
                defaults={'created_by': request.user, 'updated_by': request.user},
            )
            if created:
                added.append(student.id)
        return Response({'added': added, 'student_count': teaching_class.memberships.count()})


class TeachingClassStudentRemoveView(APIView):
    permission_classes = [IsAdminRole]

    def delete(self, request, pk, student_id):
        try:
            teaching_class = TeachingClass.objects.get(pk=pk)
        except TeachingClass.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        deleted, _ = teaching_class.memberships.filter(student_id=student_id).delete()
        if not deleted:
            return Response({'detail': 'Student not in this class.'}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeachingClassEmailView(APIView):
    """Send a class update to selected current teachers and students."""

    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            teaching_class = TeachingClass.objects.select_related(
                'teacher_1__user',
                'teacher_2__user',
            ).prefetch_related(
                Prefetch(
                    'memberships',
                    queryset=ClassMembership.objects.select_related('student__user'),
                ),
            ).get(pk=pk)
        except TeachingClass.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        teacher_ids = request.data.get('teacher_ids', [])
        student_ids = request.data.get('student_ids', [])
        if not isinstance(teacher_ids, list) or not isinstance(student_ids, list):
            return Response(
                {'detail': 'teacher_ids and student_ids must both be lists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            teacher_ids = {int(value) for value in teacher_ids}
            student_ids = {int(value) for value in student_ids}
        except (TypeError, ValueError):
            return Response({'detail': 'Recipient ids must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        class_teachers = [teacher for teacher in (teaching_class.teacher_1, teaching_class.teacher_2) if teacher]
        class_teacher_ids = {teacher.id for teacher in class_teachers}
        class_students = [membership.student for membership in teaching_class.memberships.all()]
        class_student_ids = {student.id for student in class_students}
        if not teacher_ids.issubset(class_teacher_ids) or not student_ids.issubset(class_student_ids):
            return Response(
                {'detail': 'Recipients must be current teachers or students of this class.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not teacher_ids and not student_ids:
            return Response({'detail': 'Select at least one recipient.'}, status=status.HTTP_400_BAD_REQUEST)

        teacher_names = ', '.join(
            f'{teacher.user.first_name} {teacher.user.last_name}'.strip() or teacher.user.username
            for teacher in class_teachers
        )
        student_list = '\n'.join(
            f'- {f"{student.user.first_name} {student.user.last_name}".strip() or student.user.username}'
            for student in sorted(class_students, key=lambda item: (item.user.last_name, item.user.first_name, item.user.username))
        ) or '- No students currently assigned'
        description = teaching_class.description.strip() or 'No class description has been provided.'
        subject = f'Class update: {teaching_class.name}'
        messages = []
        skipped_no_email = []

        for teacher in class_teachers:
            if teacher.id not in teacher_ids:
                continue
            if not teacher.user.email:
                skipped_no_email.append({'role': 'teacher', 'id': teacher.id})
                continue
            teacher_name = f'{teacher.user.first_name} {teacher.user.last_name}'.strip() or teacher.user.username
            messages.append((
                subject,
                f'Hello {teacher_name},\n\n'
                f'Class: {teaching_class.name}\n\n'
                f'Class description:\n{description}\n\n'
                f'Current students:\n{student_list}\n',
                settings.DEFAULT_FROM_EMAIL,
                [teacher.user.email],
            ))

        students_by_id = {student.id: student for student in class_students}
        for student_id in student_ids:
            student = students_by_id[student_id]
            if not student.user.email:
                skipped_no_email.append({'role': 'student', 'id': student.id})
                continue
            student_name = f'{student.user.first_name} {student.user.last_name}'.strip() or student.user.username
            messages.append((
                subject,
                f'Hello {student_name},\n\n'
                f'Class: {teaching_class.name}\n'
                f'Teacher{"s" if len(class_teachers) != 1 else ""}: {teacher_names or "Not assigned"}\n\n'
                f'Class description:\n{description}\n',
                settings.DEFAULT_FROM_EMAIL,
                [student.user.email],
            ))

        sent_count = send_mass_mail(messages, fail_silently=False) if messages else 0
        return Response({
            'sent_count': sent_count,
            'skipped_no_email': skipped_no_email,
        })


class ClassSessionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            teaching_class = TeachingClass.objects.get(pk=pk)
        except TeachingClass.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if not _user_can_view_class(request.user, teaching_class):
            return Response({'detail': 'Not found.'}, status=404)
        sessions = teaching_class.sessions.order_by('session_date', 'id').prefetch_related(
            'attendance_records',
        )
        return Response(ClassSessionSerializer(sessions, many=True, context={'request': request}).data)

    def post(self, request, pk):
        try:
            teaching_class = TeachingClass.objects.get(pk=pk)
        except TeachingClass.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if not (_is_admin(request.user) or _user_can_manage_class(request.user, teaching_class)):
            return Response({'detail': 'Not allowed.'}, status=403)
        if _is_student(request.user):
            return Response({'detail': 'Not allowed.'}, status=403)

        serializer = ClassSessionWriteSerializer(
            data=request.data,
            context={'teaching_class': teaching_class},
        )
        serializer.is_valid(raise_exception=True)
        session = ClassSession.objects.create(
            teaching_class=teaching_class,
            created_by=request.user,
            updated_by=request.user,
            **serializer.validated_data,
        )
        return Response(ClassSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class ClassCalendarImportView(APIView):
    """Admin-only, duplicate-safe calendar date import for one class."""

    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            teaching_class = TeachingClass.objects.get(pk=pk)
        except TeachingClass.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        dates = request.data.get('dates')
        if not isinstance(dates, list):
            return Response({'detail': 'Expected a JSON object with a dates array.'}, status=400)
        if not dates:
            return Response({'detail': 'The calendar file does not contain any dates.'}, status=400)
        if len(dates) > 1000:
            return Response({'detail': 'A maximum of 1,000 calendar dates can be imported at once.'}, status=400)

        parsed_dates = []
        errors = []
        for row, value in enumerate(dates, start=1):
            parsed = parse_date(str(value)) if isinstance(value, str) else None
            if parsed is None:
                errors.append({'row': row, 'error': 'Use the YYYY-MM-DD date format.'})
            else:
                parsed_dates.append(parsed)
        if errors:
            return Response({'detail': 'Correct the listed dates and import again.', 'errors': errors}, status=400)

        existing_dates = set(teaching_class.sessions.values_list('session_date', flat=True))
        seen_dates = set(existing_dates)
        created = []
        skipped = []
        for row, session_date in enumerate(parsed_dates, start=1):
            if session_date in seen_dates:
                skipped.append({'row': row, 'date': session_date.isoformat()})
                continue
            session = ClassSession.objects.create(
                teaching_class=teaching_class,
                session_date=session_date,
                created_by=request.user,
                updated_by=request.user,
            )
            seen_dates.add(session_date)
            created.append(session)

        return Response(
            {
                'created_count': len(created),
                'skipped_count': len(skipped),
                'created': ClassSessionSerializer(created, many=True).data,
                'skipped': skipped,
            },
            status=status.HTTP_201_CREATED,
        )


class ClassSessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get(self, request, pk):
        try:
            return ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return None

    def get(self, request, pk):
        session = self._get(request, pk)
        if not session or not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)
        return Response(ClassSessionSerializer(session, context={'request': request}).data)

    def patch(self, request, pk):
        session = self._get(request, pk)
        if not session:
            return Response({'detail': 'Not found.'}, status=404)
        if not (
            _is_admin(request.user)
            or (_is_teacher(request.user) and _user_can_manage_class(request.user, session.teaching_class))
        ):
            return Response({'detail': 'Not allowed.'}, status=403)

        if session.is_started and 'session_date' in request.data:
            new_date = request.data.get('session_date')
            if str(new_date) != str(session.session_date):
                return Response(
                    {'session_date': 'Started sessions cannot change date.'},
                    status=400,
                )

        data = request.data
        if session.is_started and hasattr(data, 'copy'):
            data = data.copy()
            data.pop('session_date', None)

        serializer = ClassSessionWriteSerializer(
            session,
            data=data,
            partial=True,
            context={'teaching_class': session.teaching_class},
        )
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            if session.is_started and field == 'session_date':
                continue
            setattr(session, field, value)
        session.updated_by = request.user
        session.save()
        return Response(ClassSessionSerializer(session).data)

    def delete(self, request, pk):
        session = self._get(request, pk)
        if not session:
            return Response({'detail': 'Not found.'}, status=404)
        if not (
            _is_admin(request.user)
            or (_is_teacher(request.user) and _user_can_manage_class(request.user, session.teaching_class))
        ):
            return Response({'detail': 'Not allowed.'}, status=403)
        if session.is_started:
            return Response(
                {'detail': 'Started sessions cannot be deleted.'},
                status=400,
            )
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassSessionStartView(APIView):
    """Teacher starts a session once → creates attendance rows for enrolled students."""

    permission_classes = [IsTeacherRole]

    def post(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not _user_can_manage_class(request.user, session.teaching_class):
            return Response({'detail': 'Not allowed.'}, status=403)
        if session.is_started:
            return Response({'detail': 'Class already started.', 'session': ClassSessionSerializer(session).data}, status=400)
        if session.session_date > timezone.localdate():
            return Response(
                {'detail': 'Future class sessions cannot be started before their date.'},
                status=400,
            )

        session.is_started = True
        session.started_at = timezone.now()
        session.updated_by = request.user
        session.save(update_fields=['is_started', 'started_at', 'updated_by', 'updated_at'])

        student_ids = session.teaching_class.memberships.values_list('student_id', flat=True)
        existing = set(
            ClassSessionAttendance.objects.filter(session=session).values_list('student_id', flat=True)
        )
        to_create = [
            ClassSessionAttendance(
                session=session,
                student_id=sid,
                status=ClassSessionAttendance.Status.NOT_MARKED,
                homework_submitted=False,
                created_by=request.user,
                updated_by=request.user,
            )
            for sid in student_ids
            if sid not in existing
        ]
        ClassSessionAttendance.objects.bulk_create(to_create)
        return Response(ClassSessionSerializer(session).data)


class ClassSessionEmailView(APIView):
    """Teacher sends the started session's classwork and homework details to students."""

    permission_classes = [IsTeacherRole]

    def post(self, request, pk):
        try:
            session = ClassSession.objects.select_related(
                'teaching_class__teacher_1__user',
                'teaching_class__teacher_2__user',
            ).prefetch_related(
                Prefetch(
                    'attendance_records',
                    queryset=ClassSessionAttendance.objects.select_related('student__user'),
                ),
                'materials',
            ).get(pk=pk)
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not _user_can_manage_class(request.user, session.teaching_class):
            return Response({'detail': 'Not allowed.'}, status=403)
        if not session.is_started:
            return Response(
                {'detail': 'Start the class before sending its attendance email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def material_details(kind):
            files = [material for material in session.materials.all() if material.kind == kind]
            if not files:
                return 'No attachments.'
            details = []
            for material in files:
                filename = material.original_filename or 'Attachment'
                url = material.file.url if material.file else ''
                if url and not url.startswith(('http://', 'https://')):
                    url = request.build_absolute_uri(url)
                details.append(f'- {filename}{f": {url}" if url else ""}')
            return '\n'.join(details)

        teacher_name = (
            f'{request.user.first_name} {request.user.last_name}'.strip()
            or request.user.username
        )
        date_label = session.session_date.strftime('%d %B %Y')
        due_date = (
            session.homework_due_date.strftime('%d %B %Y')
            if session.homework_due_date
            else 'No target date has been set.'
        )
        classwork_details = session.classwork.strip() or 'No classwork details were provided.'
        homework_details = session.homework.strip() or 'No homework details were provided.'
        classwork_files = material_details(ClassSessionMaterial.Kind.CLASSWORK)
        homework_files = material_details(ClassSessionMaterial.Kind.HOMEWORK)
        subject = f'Classwork and homework details: {session.teaching_class.name} — {date_label}'
        messages = []
        skipped_no_email = []
        emailed_student_names = []

        for attendance in session.attendance_records.all():
            student = attendance.student
            if not student.user.email:
                skipped_no_email.append(student.id)
                continue
            student_name = (
                f'{student.user.first_name} {student.user.last_name}'.strip()
                or student.user.username
            )
            emailed_student_names.append(student_name)
            messages.append((
                subject,
                f'Dear {student_name},\n\n'
                f'You are marked as {attendance.get_status_display()} for {session.teaching_class.name} on {date_label}.\n\n'
                f'The classwork details are as follows:\n{classwork_details}\n\n'
                f'Classwork attachments:\n{classwork_files}\n\n'
                f'The homework details are as follows:\n{homework_details}\n\n'
                f'Homework attachments:\n{homework_files}\n\n'
                f'Please complete the homework by: {due_date}\n\n'
                f'With best regards,\n{teacher_name}\n',
                settings.DEFAULT_FROM_EMAIL,
                [student.user.email],
            ))

        teacher_copy_sent = False
        if request.user.email:
            recipients = '\n'.join(f'- {name}' for name in emailed_student_names) or '- No students had an email address available.'
            messages.append((
                f'Class email sent: {session.teaching_class.name} — {date_label}',
                f'Hello {teacher_name},\n\n'
                f'The classwork and homework details for {session.teaching_class.name} on {date_label} '
                f'were sent to the following students:\n{recipients}\n\n'
                f'Classwork details:\n{classwork_details}\n\n'
                f'Classwork attachments:\n{classwork_files}\n\n'
                f'Homework details:\n{homework_details}\n\n'
                f'Homework attachments:\n{homework_files}\n\n'
                f'Homework target date: {due_date}\n\n'
                f'With best regards,\nBalamukundam Vidyalayam\n',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            ))
            teacher_copy_sent = True

        send_mass_mail(messages, fail_silently=False) if messages else 0
        return Response({
            'skipped_no_email_student_ids': skipped_no_email,
            'teacher_copy_sent': teacher_copy_sent,
        })


class SessionAttendanceListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)

        qs = session.attendance_records.select_related('student__user')
        if _is_student(request.user):
            student = _student_profile(request.user)
            qs = qs.filter(student=student) if student else qs.none()
        return Response(ClassSessionAttendanceSerializer(qs, many=True).data)


class SessionAttendanceUpdateView(APIView):
    """
    Teachers: update attendance status.
    Students: update own homework_submitted flag only.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, attendance_id):
        try:
            record = ClassSessionAttendance.objects.select_related(
                'session__teaching_class',
                'student__user',
            ).get(
                pk=attendance_id,
                session_id=pk,
            )
        except ClassSessionAttendance.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not record.session.is_started:
            return Response({'detail': 'Session has not started yet.'}, status=400)

        if _is_teacher(request.user) or _is_admin(request.user):
            if not _user_can_manage_class(request.user, record.session.teaching_class):
                return Response({'detail': 'Not allowed.'}, status=403)
            if 'status' not in request.data:
                return Response({'status': 'Required.'}, status=400)
            serializer = AttendanceStatusUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            record.status = serializer.validated_data['status']
            record.updated_by = request.user
            record.save(update_fields=['status', 'updated_by', 'updated_at'])
            return Response(ClassSessionAttendanceSerializer(record).data)

        if _is_student(request.user):
            student = _student_profile(request.user)
            if not student or record.student_id != student.id:
                return Response({'detail': 'Not allowed.'}, status=403)
            if 'homework_submitted' not in request.data:
                return Response({'homework_submitted': 'Required.'}, status=400)
            serializer = HomeworkSubmittedUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            record.homework_submitted = serializer.validated_data['homework_submitted']
            record.updated_by = request.user
            record.save(update_fields=['homework_submitted', 'updated_by', 'updated_at'])
            return Response(ClassSessionAttendanceSerializer(record).data)

        return Response({'detail': 'Not allowed.'}, status=403)


class SessionCommentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)

        qs = session.comments.select_related('author', 'student__user')
        student_id = request.query_params.get('student')

        if _is_student(request.user):
            student = _student_profile(request.user)
            if not student:
                return Response([])
            qs = qs.filter(student=student)
        elif student_id:
            qs = qs.filter(student_id=student_id)
        elif not (_is_admin(request.user) or _user_can_manage_class(request.user, session.teaching_class)):
            return Response({'detail': 'Not allowed.'}, status=403)

        return Response(
            ClassSessionCommentSerializer(qs, many=True, context={'request': request}).data
        )

    def post(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)

        if _is_student(request.user):
            student = _student_profile(request.user)
            if not student:
                return Response({'detail': 'Student profile required.'}, status=400)
            target_student = student
        else:
            if not (
                _is_admin(request.user)
                or _user_can_manage_class(request.user, session.teaching_class)
            ):
                return Response({'detail': 'Not allowed.'}, status=403)
            sid = request.data.get('student_id') or request.data.get('student')
            if not sid:
                return Response({'student_id': 'Required.'}, status=400)
            try:
                target_student = Student.objects.get(
                    pk=sid,
                    class_memberships__teaching_class=session.teaching_class,
                )
            except Student.DoesNotExist:
                return Response({'student_id': 'Student is not in this class.'}, status=400)

        serializer = ClassSessionCommentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = ClassSessionComment.objects.create(
            session=session,
            student=target_student,
            author=request.user,
            body=serializer.validated_data['body'],
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(
            ClassSessionCommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class SessionCommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            comment = ClassSessionComment.objects.select_related(
                'session__teaching_class',
                'author',
            ).get(pk=pk)
        except ClassSessionComment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if comment.author_id != request.user.id:
            return Response({'detail': 'You can only edit your own comments.'}, status=403)

        serializer = ClassSessionCommentWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        comment.body = serializer.validated_data['body']
        comment.updated_by = request.user
        comment.save(update_fields=['body', 'updated_by', 'updated_at'])
        return Response(ClassSessionCommentSerializer(comment, context={'request': request}).data)

    def delete(self, request, pk):
        try:
            comment = ClassSessionComment.objects.select_related(
                'session__teaching_class',
            ).get(pk=pk)
        except ClassSessionComment.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if comment.author_id != request.user.id and not _is_admin(request.user):
            return Response({'detail': 'Not allowed.'}, status=403)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionHomeworkListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)

        qs = session.homework_submissions.select_related('student__user')
        if _is_student(request.user):
            student = _student_profile(request.user)
            qs = qs.filter(student=student) if student else qs.none()
        return Response(
            ClassSessionHomeworkSerializer(qs, many=True, context={'request': request}).data
        )

    def post(self, request, pk):
        """Student uploads homework file for a session."""
        if not _is_student(request.user):
            return Response({'detail': 'Only students can upload homework.'}, status=403)

        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        student = _student_profile(request.user)
        if not student or not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)
        if not session.is_started:
            return Response(
                {'detail': 'Homework submission opens after the class is started.'},
                status=400,
            )

        upload = request.FILES.get('file')
        if not upload:
            return Response({'file': 'Required.'}, status=400)
        if upload.size > MAX_HOMEWORK_BYTES:
            return Response({'file': 'File must be 10 MB or smaller.'}, status=400)
        content_type = getattr(upload, 'content_type', '') or ''
        if content_type and content_type not in ALLOWED_HOMEWORK_TYPES:
            return Response(
                {'file': 'Allowed types: image, PDF, or audio.'},
                status=400,
            )

        hw = ClassSessionHomework.objects.create(
            session=session,
            student=student,
            file=upload,
            original_filename=getattr(upload, 'name', '')[:255],
            content_type=content_type[:100],
            storage_backend=homework_storage_backend_name(),
            created_by=request.user,
            updated_by=request.user,
        )
        apply_storage_metadata(hw)
        return Response(
            ClassSessionHomeworkSerializer(hw, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class SessionHomeworkEmailView(APIView):
    """Student sends their session homework submission links to the class teachers."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not _is_student(request.user):
            return Response({'detail': 'Only students can send homework submission emails.'}, status=403)

        try:
            session = ClassSession.objects.select_related(
                'teaching_class__teacher_1__user',
                'teaching_class__teacher_2__user',
            ).get(pk=pk)
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        student = _student_profile(request.user)
        if not student or not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)
        if not session.is_started:
            return Response({'detail': 'Start the class before sending homework submissions.'}, status=400)

        submissions = list(
            session.homework_submissions.filter(student=student).order_by('created_at', 'id')
        )
        comments = list(
            session.comments.filter(student=student).select_related('author').order_by('created_at', 'id')
        )
        if not submissions and not comments:
            return Response(
                {'detail': 'Add a communication note or upload a homework file before sending.'},
                status=400,
            )

        attachment_details = []
        for submission in submissions:
            filename = submission.original_filename or 'Homework attachment'
            url = submission.file.url if submission.file else ''
            if url and not url.startswith(('http://', 'https://')):
                url = request.build_absolute_uri(url)
            attachment_details.append(f'- {filename}{f": {url}" if url else ""}')
        attachments = '\n'.join(attachment_details)
        communication_notes = '\n'.join(
            f'- {comment.author.get_full_name() or comment.author.username}: {comment.body}'
            for comment in comments
        )
        submission_details = []
        if communication_notes:
            submission_details.append(f'Communication notes:\n{communication_notes}')
        if attachments:
            submission_details.append(f'Homework attachments:\n{attachments}')
        content_details = '\n\n'.join(submission_details)
        student_name = f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username
        date_label = session.session_date.strftime('%d %B %Y')
        teacher_recipients = [
            teacher.user.email
            for teacher in (session.teaching_class.teacher_1, session.teaching_class.teacher_2)
            if teacher and teacher.user.email
        ]
        if not teacher_recipients:
            return Response(
                {'detail': 'No email address is available for this class teacher.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subject = f'Homework submission of {student_name} for {session.teaching_class.name} — {date_label}'
        messages = []
        if teacher_recipients:
            messages.append((
                subject,
                f'Dear Teacher,\n\n'
                f'{student_name} has submitted homework for {session.teaching_class.name} on {date_label}.\n\n'
                f'{content_details}\n\n'
                f'With best regards,\nBalamukundam Vidyalayam\n',
                settings.DEFAULT_FROM_EMAIL,
                teacher_recipients,
            ))
        student_copy_sent = False
        if request.user.email:
            messages.append((
                f'Homework submission confirmation: {session.teaching_class.name} — {date_label}',
                f'Dear {student_name},\n\n'
                f'Your homework for {session.teaching_class.name} on {date_label} has been submitted to the teacher.\n\n'
                f'{content_details}\n\n'
                f'With best regards,\nBalamukundam Vidyalayam\n',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            ))
            student_copy_sent = True

        send_mass_mail(messages, fail_silently=False) if messages else 0
        attendance = ClassSessionAttendance.objects.filter(session=session, student=student).first()
        if attendance and not attendance.homework_submitted:
            attendance.homework_submitted = True
            attendance.updated_by = request.user
            attendance.save(update_fields=['homework_submitted', 'updated_by', 'updated_at'])
        return Response({
            'teacher_email_sent': bool(teacher_recipients),
            'student_copy_sent': student_copy_sent,
            'homework_submitted': bool(attendance and attendance.homework_submitted),
        })


class SessionHomeworkDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        """Teacher adds feedback on a homework submission."""
        try:
            hw = ClassSessionHomework.objects.select_related(
                'session__teaching_class',
                'student__user',
            ).get(pk=pk)
        except ClassSessionHomework.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not (
            _is_admin(request.user)
            or (_is_teacher(request.user) and _user_can_manage_class(request.user, hw.session.teaching_class))
        ):
            return Response({'detail': 'Not allowed.'}, status=403)

        serializer = HomeworkFeedbackSerializer(hw, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        hw.teacher_feedback = serializer.validated_data.get('teacher_feedback', hw.teacher_feedback)
        hw.updated_by = request.user
        hw.save(update_fields=['teacher_feedback', 'updated_by', 'updated_at'])
        return Response(ClassSessionHomeworkSerializer(hw, context={'request': request}).data)


class SessionMaterialListCreateView(APIView):
    """Teachers upload classwork/homework files; students and teachers can list them."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if not _user_can_view_class(request.user, session.teaching_class):
            return Response({'detail': 'Not found.'}, status=404)

        qs = session.materials.all()
        kind = request.query_params.get('kind')
        if kind in (ClassSessionMaterial.Kind.CLASSWORK, ClassSessionMaterial.Kind.HOMEWORK):
            qs = qs.filter(kind=kind)
        return Response(
            ClassSessionMaterialSerializer(qs, many=True, context={'request': request}).data
        )

    def post(self, request, pk):
        try:
            session = ClassSession.objects.select_related('teaching_class').get(
                pk=pk,
            )
        except ClassSession.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not (
            _is_admin(request.user)
            or (_is_teacher(request.user) and _user_can_manage_class(request.user, session.teaching_class))
        ):
            return Response({'detail': 'Not allowed.'}, status=403)

        kind = (request.data.get('kind') or '').upper()
        if kind not in (ClassSessionMaterial.Kind.CLASSWORK, ClassSessionMaterial.Kind.HOMEWORK):
            return Response({'kind': 'Must be CLASSWORK or HOMEWORK.'}, status=400)

        upload = request.FILES.get('file')
        if not upload:
            return Response({'file': 'Required.'}, status=400)
        if upload.size > MAX_MATERIAL_BYTES:
            return Response({'file': 'File must be 20 MB or smaller.'}, status=400)
        content_type = getattr(upload, 'content_type', '') or ''
        if content_type and content_type not in ALLOWED_MATERIAL_TYPES:
            return Response(
                {'file': 'Allowed types: image, PDF, audio, Word, PowerPoint, or text.'},
                status=400,
            )

        material = ClassSessionMaterial.objects.create(
            session=session,
            kind=kind,
            file=upload,
            original_filename=getattr(upload, 'name', '')[:255],
            content_type=content_type[:100],
            storage_backend=homework_storage_backend_name(),
            created_by=request.user,
            updated_by=request.user,
        )
        apply_storage_metadata(material)
        return Response(
            ClassSessionMaterialSerializer(material, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class SessionMaterialDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            material = ClassSessionMaterial.objects.select_related(
                'session__teaching_class',
            ).get(pk=pk)
        except ClassSessionMaterial.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if not (
            _is_admin(request.user)
            or (
                _is_teacher(request.user)
                and _user_can_manage_class(request.user, material.session.teaching_class)
            )
        ):
            return Response({'detail': 'Not allowed.'}, status=403)

        delete_stored_file(material)
        material.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
