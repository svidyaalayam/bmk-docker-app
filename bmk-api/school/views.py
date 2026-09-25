import json
from datetime import timezone as datetime_timezone
from email.utils import parsedate_to_datetime

from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdminRole
from authentication.serializers import UserSerializer
from authentication.usernames import username_for_school_email
from .birthday_snapshots import get_daily_birthday_snapshot
from .models import AdminRequest, Course, CourseClass, Student, StudentTeacherRequest, Teacher, TeachingClass
from .serializers import (
    HomepageContentSerializer,
    SchoolSettingsSerializer,
    StudentSerializer,
    StudentUpdateSerializer,
    TeacherSerializer,
    TeacherUpdateSerializer,
    AdminRequestSerializer,
    StudentTeacherRequestSerializer,
)
from .tenancy import resolve_school

User = get_user_model()


class HomepageContentView(APIView):
    """Public homepage payload for one school."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings = resolve_school(request, required=True)
        courses = Course.objects.filter(is_published=True, is_active=True).prefetch_related(
            Prefetch(
                'classes',
                queryset=CourseClass.objects.filter(is_published=True, is_active=True),
            )
        )
        payload = {
            'school': settings,
            'courses': courses,
            'birthdays': get_daily_birthday_snapshot().birthday_students,
        }
        return Response(HomepageContentSerializer(payload).data)


class SchoolSettingsPublicView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings = resolve_school(request, required=True)
        return Response(SchoolSettingsSerializer(settings).data)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = User.objects.all().order_by('role', 'username')
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role.upper())
        return queryset


class AdminUserCreateView(APIView):
    """User creation by admins is disabled — registration only."""

    permission_classes = [IsAdminRole]

    def post(self, request):
        return Response(
            {'detail': 'Admins cannot create users. Users must register themselves.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class UserAdminRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == User.Roles.ADMIN:
            return Response({'detail': 'Admin accounts do not have user requests.'}, status=400)
        items = AdminRequest.objects.filter(
            user=request.user,
        ).select_related('user', 'replied_by')[:10]
        return Response(AdminRequestSerializer(items, many=True).data)

    def post(self, request):
        if request.user.role == User.Roles.ADMIN:
            return Response({'detail': 'Admin accounts cannot submit user requests.'}, status=400)
        kind = request.data.get('kind')
        subject = str(request.data.get('subject') or '').strip()
        message = str(request.data.get('message') or '').strip()
        if kind not in AdminRequest.Kind.values:
            return Response({'kind': 'Choose Request or Feedback / suggestion.'}, status=400)
        if not subject or not message:
            return Response({'detail': 'A subject and message are required.'}, status=400)
        item = AdminRequest.objects.create(user=request.user, kind=kind, subject=subject, message=message)
        return Response(AdminRequestSerializer(item).data, status=status.HTTP_201_CREATED)


class AdminRequestListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        queryset = AdminRequest.objects.all().select_related('user', 'replied_by')
        if request.query_params.get('status') == 'open':
            queryset = queryset.filter(resolved=False)
        elif request.query_params.get('status') == 'resolved':
            queryset = queryset.filter(resolved=True)
        kind = request.query_params.get('kind')
        if kind in AdminRequest.Kind.values:
            queryset = queryset.filter(kind=kind)
        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = min(100, max(5, int(request.query_params.get('page_size', 20))))
        except ValueError:
            return Response({'detail': 'page and page_size must be whole numbers.'}, status=400)
        total = queryset.count()
        start = (page - 1) * page_size
        return Response({'count': total, 'page': page, 'page_size': page_size, 'results': AdminRequestSerializer(queryset[start:start + page_size], many=True).data})


class AdminRequestDetailView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        try:
            item = AdminRequest.objects.select_related('user', 'replied_by').get(pk=pk)
        except AdminRequest.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        if 'reply' in request.data:
            item.reply = str(request.data['reply']).strip()
            item.replied_by = request.user
        if 'resolved' in request.data:
            item.resolved = bool(request.data['resolved'])
            item.resolved_at = timezone.now() if item.resolved else None
        item.save()
        return Response(AdminRequestSerializer(item).data)


class StudentTeacherRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Roles.STUDENT:
            return Response({'detail': 'Student access required.'}, status=403)
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({'detail': 'Student profile required.'}, status=400)
        items = StudentTeacherRequest.objects.filter(student=student).select_related('student__user', 'teaching_class', 'replied_by')[:10]
        return Response(StudentTeacherRequestSerializer(items, many=True).data)

    def post(self, request):
        if request.user.role != User.Roles.STUDENT:
            return Response({'detail': 'Student access required.'}, status=403)
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({'detail': 'Student profile required.'}, status=400)
        try:
            teaching_class = TeachingClass.objects.get(
                pk=request.data.get('class_id'), memberships__student=student, is_active=True,
            )
        except (TeachingClass.DoesNotExist, TypeError, ValueError):
            return Response({'class_id': 'Choose one of your active classes.'}, status=400)
        kind = request.data.get('kind'); subject = str(request.data.get('subject') or '').strip(); message = str(request.data.get('message') or '').strip()
        if kind not in StudentTeacherRequest.Kind.values:
            return Response({'kind': 'Choose Request or Feedback / suggestion.'}, status=400)
        if not subject or not message:
            return Response({'detail': 'A subject and message are required.'}, status=400)
        item = StudentTeacherRequest.objects.create(teaching_class=teaching_class, student=student, kind=kind, subject=subject, message=message)
        return Response(StudentTeacherRequestSerializer(item).data, status=status.HTTP_201_CREATED)


class TeacherRequestListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Roles.TEACHER:
            return Response({'detail': 'Teacher access required.'}, status=403)
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher:
            return Response({'detail': 'Teacher profile required.'}, status=400)
        queryset = StudentTeacherRequest.objects.filter(Q(teaching_class__teacher_1=teacher) | Q(teaching_class__teacher_2=teacher)).select_related('student__user', 'teaching_class', 'replied_by')
        if request.query_params.get('status') == 'open': queryset = queryset.filter(resolved=False)
        elif request.query_params.get('status') == 'resolved': queryset = queryset.filter(resolved=True)
        try: page = max(1, int(request.query_params.get('page', 1)))
        except ValueError: return Response({'detail': 'page must be a whole number.'}, status=400)
        total = queryset.count(); start = (page - 1) * 20
        return Response({'count': total, 'page': page, 'page_size': 20, 'results': StudentTeacherRequestSerializer(queryset[start:start + 20], many=True).data})


class TeacherRequestDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != User.Roles.TEACHER: return Response({'detail': 'Teacher access required.'}, status=403)
        teacher = getattr(request.user, 'teacher_profile', None)
        try: item = StudentTeacherRequest.objects.select_related('student__user', 'teaching_class', 'replied_by').get(pk=pk)
        except StudentTeacherRequest.DoesNotExist: return Response({'detail': 'Not found.'}, status=404)
        if not teacher or (item.teaching_class.teacher_1_id != teacher.id and item.teaching_class.teacher_2_id != teacher.id): return Response({'detail': 'Not allowed.'}, status=403)
        if 'reply' in request.data: item.reply = str(request.data['reply']).strip(); item.replied_by = request.user
        if 'resolved' in request.data: item.resolved = bool(request.data['resolved']); item.resolved_at = timezone.now() if item.resolved else None
        item.save(); return Response(StudentTeacherRequestSerializer(item).data)


class FirebaseUserImportView(APIView):
    """Import legacy Firebase users for the authenticated admin's school."""

    permission_classes = [IsAdminRole]
    max_file_size = 5 * 1024 * 1024
    max_users = 5000

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if uploaded_file is None:
            return Response({'detail': 'Provide the JSON file in the "file" field.'}, status=400)
        if not uploaded_file.name.lower().endswith('.json'):
            return Response({'detail': 'Upload a file with a .json extension.'}, status=400)
        if uploaded_file.size > self.max_file_size:
            return Response({'detail': 'The JSON file must be 5 MB or smaller.'}, status=400)

        try:
            records = json.loads(uploaded_file.read().decode('utf-8-sig'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return Response({'detail': 'The uploaded file is not valid UTF-8 JSON.'}, status=400)

        if not isinstance(records, list):
            return Response({'detail': 'The JSON file must contain an array of users.'}, status=400)
        if not records:
            return Response({'detail': 'The JSON file does not contain any users.'}, status=400)
        if len(records) > self.max_users:
            return Response({'detail': f'A maximum of {self.max_users} users can be imported at once.'}, status=400)
        prepared_users = []
        errors = []
        duplicate_rows = []
        seen_uids = set()
        seen_emails = set()
        for number, record in enumerate(records, start=1):
            try:
                prepared = self._prepare_record(record)
                email = prepared['email'].lower()
                if prepared['legacy_uid'] in seen_uids or email in seen_emails:
                    duplicate_rows.append(
                        {
                            'row': number,
                            'email': prepared['email'],
                            'reason': 'Duplicated in the uploaded file.',
                        }
                    )
                    continue
                seen_uids.add(prepared['legacy_uid'])
                seen_emails.add(email)
                prepared['_source_row'] = number
                prepared_users.append(prepared)
            except ValueError as exc:
                errors.append({'row': number, 'error': str(exc)})

        if errors:
            return Response(
                {
                    'detail': 'Import rejected. Correct the listed rows and upload the file again.',
                    'errors': errors,
                },
                status=400,
            )

        for data in prepared_users:
            number = data['_source_row']
            existing = self._existing_user(data)
            if existing:
                reason = (
                    'Firebase ID already exists.'
                    if existing.legacy_uid == data['legacy_uid']
                    else 'Email address already exists.'
                )
                duplicate_rows.append({'row': number, 'email': data['email'], 'reason': reason})

        if duplicate_rows and request.query_params.get('duplicate_action') != 'skip':
            return Response(
                {
                    'detail': (
                        'Duplicate users were found. No users have been imported yet. '
                        'Continue to import only the remaining users, or cancel.'
                    ),
                    'duplicate_count': len(duplicate_rows),
                    'duplicates': duplicate_rows,
                },
                status=status.HTTP_409_CONFLICT,
            )

        created = []
        skipped = list(duplicate_rows)
        created_by_role = {
            User.Roles.STUDENT: 0,
            User.Roles.TEACHER: 0,
            User.Roles.ADMIN: 0,
        }
        with transaction.atomic():
            for data in prepared_users:
                number = data.pop('_source_row')
                existing = self._existing_user(data)
                if existing:
                    continue

                profile_data = data.pop('profile', None)
                user = User(
                    username=username_for_school_email(data['email'], resolve_school(request, required=True)),
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=data['phone_number'] or None,
                    role=data['role'],
                    email_verified=data['email_verified'],
                    is_active=data['is_active'],
                    legacy_uid=data['legacy_uid'],
                )
                # Firebase password hashes are deliberately not imported. Users set a new
                # password through the normal password-reset flow before their first login.
                user.set_unusable_password()
                user.save()
                # auto_now_add always writes the current timestamp during the first save.
                # Apply the legacy Firebase timestamps immediately afterwards instead.
                update_fields = []
                if data['creation_time'] is not None:
                    user.date_joined = data['creation_time']
                    update_fields.append('date_joined')
                if data['last_sign_in_time'] is not None:
                    user.last_login = data['last_sign_in_time']
                    update_fields.append('last_login')
                if update_fields:
                    user.save(update_fields=update_fields)

                if profile_data is not None:
                    profile_model = Teacher if data['role'] == User.Roles.TEACHER else Student
                    profile_model.objects.create(
                        user=user,
                        is_active=data['is_active'],
                        created_by=request.user,
                        updated_by=request.user,
                        **profile_data,
                )
                created.append({'row': number, 'id': user.id, 'email': user.email, 'role': user.role})
                created_by_role[user.role] += 1

        return Response(
            {
                'created_count': len(created),
                'skipped_count': len(skipped),
                'created_by_role': created_by_role,
                'created': created,
                'skipped': skipped,
                'password_note': (
                    'Imported users must use the password-reset flow to create a password before signing in.'
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _existing_user(data):
        return User.objects.filter(
            Q(username__iexact=data['email'])
            | Q(email__iexact=data['email'])
            | Q(legacy_uid=data['legacy_uid']),
        ).first()

    @staticmethod
    def _prepare_record(record):
        if not isinstance(record, dict):
            raise ValueError('Each array entry must be an object.')
        auth = record.get('auth') or {}
        firestore = record.get('firestore') or {}
        if not isinstance(auth, dict) or not isinstance(firestore, dict):
            raise ValueError('The auth and firestore values must be objects.')

        email = str(record.get('email') or firestore.get('loginid') or '').strip().lower()
        if not email:
            raise ValueError('An email or firestore.loginid is required.')
        try:
            validate_email(email)
        except Exception:
            raise ValueError('The email address is invalid.')
        if len(email) > 150:
            raise ValueError('The email address is too long to use as a username.')

        legacy_uid = str(record.get('uid') or '').strip()
        if not legacy_uid:
            raise ValueError('A Firebase uid is required.')
        if len(legacy_uid) > 128:
            raise ValueError('The Firebase uid is too long.')

        role = FirebaseUserImportView._role_for(firestore.get('usertype'))
        gender = (
            FirebaseUserImportView._gender_for(firestore.get('gender'), role)
            if role != User.Roles.ADMIN
            else None
        )
        date_of_birth = FirebaseUserImportView._date_for(firestore.get('dob'))
        creation_time = FirebaseUserImportView._timestamp_for(auth.get('creationTime'), 'auth.creationTime')
        last_sign_in_time = FirebaseUserImportView._timestamp_for(
            auth.get('lastSignInTime'), 'auth.lastSignInTime'
        )
        disabled = bool(auth.get('disabled', False)) or bool(firestore.get('accountsuspended', False))
        is_active = not disabled

        first_name = str(firestore.get('name') or auth.get('displayName') or '').strip()
        last_name = str(firestore.get('surname') or '').strip()
        if not first_name and not last_name:
            raise ValueError('A name is required (firestore.name or auth.displayName).')

        base = {
            'legacy_uid': legacy_uid,
            'email': email,
            'first_name': first_name[:150],
            'last_name': last_name[:150],
            'phone_number': str(firestore.get('contactnumber') or auth.get('phoneNumber') or '').strip()[:15],
            'role': role,
            'email_verified': bool(auth.get('emailVerified', False)),
            'is_active': is_active,
            'creation_time': creation_time,
            'last_sign_in_time': last_sign_in_time,
        }
        if role == User.Roles.TEACHER:
            base['profile'] = {'gender': gender, 'phone': base['phone_number'][:20]}
        elif role == User.Roles.STUDENT:
            notes = '\n'.join(
                f'{label}: {value}'
                for label, value in (
                    ('Additional information', firestore.get('additionalinfo')),
                    ('Admin comments', firestore.get('admincomments')),
                    ('Teacher name', firestore.get('teachername')),
                )
                if value
            )
            base['profile'] = {
                'gender': gender,
                'date_of_birth': date_of_birth,
                'phone': base['phone_number'][:20],
                'parent_name': str(firestore.get('parentsname') or '').strip()[:100],
                'parent_phone': str(firestore.get('whatsappnumber') or '').strip()[:20],
                'address': str(firestore.get('city') or '').strip(),
                'notes': notes,
            }
        return base

    @staticmethod
    def _role_for(user_type):
        if str(user_type).strip() == '0':
            return User.Roles.STUDENT
        if str(user_type).strip() == '1':
            return User.Roles.TEACHER
        if str(user_type).strip() == '2':
            return User.Roles.ADMIN
        raise ValueError('Unsupported firestore.usertype. Use 0 for students, 1 for teachers, or 2 for admins.')

    @staticmethod
    def _gender_for(value, role):
        normalized = str(value or '').strip().lower()
        if normalized in {'boy', 'male', 'm'}:
            return 'M'
        if normalized in {'girl', 'female', 'f'}:
            return 'F'
        label = 'teacher' if role == User.Roles.TEACHER else 'student'
        raise ValueError(f'A recognised gender is required for each {label} (Boy/Girl or Male/Female).')

    @staticmethod
    def _date_for(value):
        if value in (None, ''):
            return None
        parsed = parse_date(str(value))
        if parsed is None:
            raise ValueError('firestore.dob must be blank or formatted as YYYY-MM-DD.')
        return parsed

    @staticmethod
    def _timestamp_for(value, field_name):
        if value in (None, ''):
            return None
        text = str(value).strip()
        parsed = parse_datetime(text)
        if parsed is None:
            try:
                parsed = parsedate_to_datetime(text)
            except (TypeError, ValueError, IndexError):
                parsed = None
        if parsed is None:
            raise ValueError(f'{field_name} must be a valid timestamp.')
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, datetime_timezone.utc)
        return parsed


class TeacherListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = TeacherSerializer

    def get_queryset(self):
        return (
            Teacher.objects.all()
            .select_related('user')
            .annotate(
                class_assignment_count=Count(
                    'classes_as_primary', filter=Q(classes_as_primary__is_active=True), distinct=True
                )
                + Count(
                    'classes_as_secondary', filter=Q(classes_as_secondary__is_active=True), distinct=True
                )
            )
        )


class TeacherDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminRole]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        return Teacher.objects.all().select_related('user')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TeacherUpdateSerializer
        return TeacherSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(TeacherSerializer(teacher).data)


class StudentListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = StudentSerializer

    def get_queryset(self):
        return (
            Student.objects.all()
            .select_related('user')
            .annotate(
                class_assignment_count=Count(
                    'class_memberships', filter=Q(class_memberships__teaching_class__is_active=True), distinct=True
                )
            )
        )


class StudentDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminRole]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        return Student.objects.all().select_related('user')

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return StudentUpdateSerializer
        return StudentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response(StudentSerializer(student).data)
