from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    ClassMembership,
    ClassSession,
    ClassSessionAttendance,
    ClassSessionComment,
    ClassSessionHomework,
    ClassSessionMaterial,
    Student,
    Teacher,
    TeachingClass,
)
from .storage import file_access_url

User = get_user_model()


class StudentBriefSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class TeacherBriefSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Teacher
        fields = ('id', 'username', 'first_name', 'last_name')


class ClassSessionSerializer(serializers.ModelSerializer):
    present_count = serializers.SerializerMethodField()
    attendance_total = serializers.SerializerMethodField()
    my_attendance_status = serializers.SerializerMethodField()

    class Meta:
        model = ClassSession
        fields = (
            'id',
            'teaching_class',
            'session_date',
            'classwork',
            'homework',
            'is_started',
            'started_at',
            'present_count',
            'attendance_total',
            'my_attendance_status',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'teaching_class',
            'is_started',
            'started_at',
            'present_count',
            'attendance_total',
            'my_attendance_status',
            'created_at',
            'updated_at',
        )

    def get_present_count(self, obj):
        request = self.context.get('request')
        if request and getattr(request.user, 'role', None) == request.user.Roles.STUDENT:
            return None
        if not obj.is_started:
            return 0
        records = getattr(obj, '_prefetched_objects_cache', {}).get('attendance_records')
        if records is not None:
            return sum(1 for r in records if r.status == ClassSessionAttendance.Status.PRESENT)
        return obj.attendance_records.filter(status=ClassSessionAttendance.Status.PRESENT).count()

    def get_attendance_total(self, obj):
        request = self.context.get('request')
        if request and getattr(request.user, 'role', None) == request.user.Roles.STUDENT:
            return None
        if not obj.is_started:
            return 0
        records = getattr(obj, '_prefetched_objects_cache', {}).get('attendance_records')
        if records is not None:
            return len(records)
        return obj.attendance_records.count()

    def get_my_attendance_status(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None
        if getattr(user, 'role', None) != user.Roles.STUDENT or not obj.is_started:
            return None
        student = getattr(user, 'student_profile', None)
        if not student:
            return None
        records = getattr(obj, '_prefetched_objects_cache', {}).get('attendance_records')
        if records is not None:
            for record in records:
                if record.student_id == student.id:
                    return record.status
            return None
        record = obj.attendance_records.filter(student=student).only('status').first()
        return record.status if record else None



class ClassSessionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = ('session_date', 'classwork', 'homework')

    def validate_session_date(self, value):
        teaching_class = self.context['teaching_class']
        qs = ClassSession.objects.filter(teaching_class=teaching_class, session_date=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A session already exists on this date.')
        return value


class TeachingClassListSerializer(serializers.ModelSerializer):
    teacher_1 = TeacherBriefSerializer(read_only=True)
    teacher_2 = TeacherBriefSerializer(read_only=True)
    student_count = serializers.SerializerMethodField()
    session_count = serializers.SerializerMethodField()

    class Meta:
        model = TeachingClass
        fields = (
            'id',
            'name',
            'description',
            'teacher_1',
            'teacher_2',
            'student_count',
            'session_count',
            'is_active',
            'created_at',
            'updated_at',
        )

    def get_student_count(self, obj):
        if hasattr(obj, '_student_count'):
            return obj._student_count
        return obj.memberships.count()

    def get_session_count(self, obj):
        if hasattr(obj, '_session_count'):
            return obj._session_count
        return obj.sessions.count()


class TeachingClassDetailSerializer(serializers.ModelSerializer):
    teacher_1 = TeacherBriefSerializer(read_only=True)
    teacher_2 = TeacherBriefSerializer(read_only=True)
    teacher_1_id = serializers.PrimaryKeyRelatedField(
        source='teacher_1',
        queryset=Teacher.objects.all(),
        write_only=True,
    )
    teacher_2_id = serializers.PrimaryKeyRelatedField(
        source='teacher_2',
        queryset=Teacher.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
    )
    students = StudentBriefSerializer(many=True, read_only=True)
    sessions = ClassSessionSerializer(many=True, read_only=True)
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = TeachingClass
        fields = (
            'id',
            'name',
            'description',
            'teacher_1',
            'teacher_2',
            'teacher_1_id',
            'teacher_2_id',
            'students',
            'student_ids',
            'sessions',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at')

    def validate(self, attrs):
        school = self.context['school']
        teacher_1 = attrs.get('teacher_1') or getattr(self.instance, 'teacher_1', None)
        teacher_2 = attrs.get('teacher_2', serializers.empty)
        if teacher_2 is serializers.empty:
            teacher_2 = getattr(self.instance, 'teacher_2', None) if self.instance else None

        if teacher_1 and teacher_1.school_id != school.id:
            raise serializers.ValidationError({'teacher_1_id': 'Teacher must belong to this school.'})
        if teacher_2 and teacher_2.school_id != school.id:
            raise serializers.ValidationError({'teacher_2_id': 'Teacher must belong to this school.'})
        if teacher_1 and teacher_2 and teacher_1.pk == teacher_2.pk:
            raise serializers.ValidationError({'teacher_2_id': 'Teacher 2 must differ from teacher 1.'})

        name = attrs.get('name')
        if name:
            qs = TeachingClass.objects.filter(school=school, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'name': 'A class with this name already exists.'})
        return attrs

    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids', [])
        school = self.context['school']
        user = self.context['request'].user
        teaching_class = TeachingClass.objects.create(
            school=school,
            created_by=user,
            updated_by=user,
            **validated_data,
        )
        self._sync_students(teaching_class, student_ids, user)
        return teaching_class

    def update(self, instance, validated_data):
        student_ids = validated_data.pop('student_ids', None)
        user = self.context['request'].user
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.updated_by = user
        instance.save()
        if student_ids is not None:
            self._sync_students(instance, student_ids, user)
        return instance

    def _sync_students(self, teaching_class, student_ids, user):
        school = teaching_class.school
        wanted = set(
            Student.objects.filter(school=school, pk__in=student_ids).values_list('id', flat=True)
        )
        existing = set(teaching_class.memberships.values_list('student_id', flat=True))
        for sid in wanted - existing:
            ClassMembership.objects.create(
                teaching_class=teaching_class,
                student_id=sid,
                created_by=user,
                updated_by=user,
            )
        teaching_class.memberships.filter(student_id__in=existing - wanted).delete()


class TeachingClassTeacherUpdateSerializer(serializers.ModelSerializer):
    """Teachers may only edit description."""

    class Meta:
        model = TeachingClass
        fields = ('description',)


class ClassSessionAttendanceSerializer(serializers.ModelSerializer):
    student = StudentBriefSerializer(read_only=True)

    class Meta:
        model = ClassSessionAttendance
        fields = ('id', 'session', 'student', 'status', 'homework_submitted', 'updated_at')
        read_only_fields = ('id', 'session', 'student', 'updated_at')


class AttendanceStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ClassSessionAttendance.Status.choices)


class HomeworkSubmittedUpdateSerializer(serializers.Serializer):
    homework_submitted = serializers.BooleanField()


class ClassSessionCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)
    author_name = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = ClassSessionComment
        fields = (
            'id',
            'session',
            'student',
            'author',
            'author_username',
            'author_role',
            'author_name',
            'body',
            'can_edit',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'session',
            'student',
            'author',
            'created_at',
            'updated_at',
        )

    def get_author_name(self, obj):
        name = f'{obj.author.first_name} {obj.author.last_name}'.strip()
        return name or obj.author.username

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return bool(request and request.user and request.user.pk == obj.author_id)


class ClassSessionCommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSessionComment
        fields = ('body',)

    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Comment cannot be empty.')
        return value.strip()


class ClassSessionHomeworkSerializer(serializers.ModelSerializer):
    student = StudentBriefSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ClassSessionHomework
        fields = (
            'id',
            'session',
            'student',
            'original_filename',
            'content_type',
            'file_url',
            'storage_backend',
            'storage_uri',
            'teacher_feedback',
            'ai_evaluation_status',
            'ai_evaluation_notes',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        return file_access_url(obj)


class HomeworkFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSessionHomework
        fields = ('teacher_feedback',)


class ClassSessionMaterialSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ClassSessionMaterial
        fields = (
            'id',
            'session',
            'kind',
            'original_filename',
            'content_type',
            'file_url',
            'storage_backend',
            'storage_uri',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        return file_access_url(obj)
