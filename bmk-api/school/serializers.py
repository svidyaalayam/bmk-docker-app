from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from authentication.serializers import UserSerializer
from .models import (
    AdminRequest,
    AcademicCalendarEntry,
    Announcement,
    Course,
    CourseClass,
    SchoolSettings,
    Student,
    StudentTeacherRequest,
    Teacher,
)

User = get_user_model()


class CourseClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseClass
        fields = (
            'id',
            'name',
            'display_order',
            'aim',
            'conditions',
            'curriculum',
            'aim_secondary',
            'conditions_secondary',
            'curriculum_secondary',
        )


class CourseSerializer(serializers.ModelSerializer):
    classes = CourseClassSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'summary', 'display_order', 'display_language', 'classes')


class AcademicCalendarEntrySerializer(serializers.ModelSerializer):
    term_name = serializers.SerializerMethodField()

    class Meta:
        model = AcademicCalendarEntry
        fields = (
            'id',
            'term_name',
            'entry_type',
            'title',
            'start_date',
            'end_date',
            'notes',
        )

    def get_term_name(self, obj):
        return obj.term.name if obj.term_id else 'Other dates'


class AnnouncementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = (
            'id',
            'title',
            'message',
            'image_url',
            'start_date',
            'end_date',
        )

    def get_image_url(self, obj):
        if not obj.image:
            return None
        return obj.image.url


class SchoolSettingsSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source='id', read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolSettings
        fields = (
            'school_id',
            'school_slug',
            'school_name',
            'lesson_app',
            'logo_url',
            'tagline',
            'introduction',
            'secondary_language',
            'introduction_secondary',
            'footer_text',
            'terms_and_conditions',
            'updated_at',
        )

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        # Relative /media/... path works with Vite/Nginx proxies.
        return obj.logo.url


class HomepageContentSerializer(serializers.Serializer):
    school = SchoolSettingsSerializer()
    courses = CourseSerializer(many=True)
    academic_calendar = AcademicCalendarEntrySerializer(many=True)
    announcements = AnnouncementSerializer(many=True)
    birthdays = serializers.ListField(child=serializers.DictField())


class AdminRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replied_by_name = serializers.CharField(source='replied_by.username', read_only=True, default=None)

    class Meta:
        model = AdminRequest
        fields = ('id', 'user', 'kind', 'subject', 'message', 'reply', 'replied_by_name', 'resolved', 'resolved_at', 'created_at', 'updated_at')


class StudentTeacherRequestSerializer(serializers.ModelSerializer):
    student = UserSerializer(source='student.user', read_only=True)
    class_name = serializers.CharField(source='teaching_class.name', read_only=True)
    replied_by_name = serializers.CharField(source='replied_by.username', read_only=True, default=None)

    class Meta:
        model = StudentTeacherRequest
        fields = ('id', 'student', 'teaching_class', 'class_name', 'kind', 'subject', 'message', 'reply', 'replied_by_name', 'resolved', 'resolved_at', 'created_at', 'updated_at')


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class_assignment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Student
        fields = (
            'id',
            'user',
            'gender',
            'date_of_birth',
            'phone',
            'parent_name',
            'parent_phone',
            'address',
            'notes',
            'account_blocked',
            'block_reason',
            'is_active',
            'created_at',
            'updated_at',
            'class_assignment_count',
        )
        read_only_fields = ('id', 'user', 'is_active', 'created_at', 'updated_at')


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class_assignment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Teacher
        fields = (
            'id',
            'user',
            'gender',
            'phone',
            'is_active',
            'created_at',
            'updated_at',
            'class_assignment_count',
        )
        read_only_fields = ('id', 'user', 'is_active', 'created_at', 'updated_at')


class StudentUpdateSerializer(serializers.Serializer):
    """Admin edit of student details — no password, username stays read-only."""

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.ChoiceField(choices=Student.Gender.choices, required=False)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    parent_name = serializers.CharField(required=False, allow_blank=True)
    parent_phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    account_blocked = serializers.BooleanField(required=False)
    block_reason = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context['request']
        user = instance.user
        for field in ('first_name', 'last_name', 'email', 'phone_number'):
            if field in validated_data:
                setattr(user, field, validated_data.pop(field) or ('' if field != 'phone_number' else None))
        if 'is_active' in validated_data:
            is_active = validated_data.pop('is_active')
            user.is_active = is_active
            instance.is_active = is_active
        user.save()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.updated_by = request.user
        instance.save()
        return instance


class TeacherUpdateSerializer(serializers.Serializer):
    """Admin edit of teacher details — no password, username stays read-only."""

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.ChoiceField(choices=Teacher.Gender.choices, required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context['request']
        user = instance.user
        for field in ('first_name', 'last_name', 'email', 'phone_number'):
            if field in validated_data:
                setattr(user, field, validated_data.pop(field) or ('' if field != 'phone_number' else None))
        if 'is_active' in validated_data:
            is_active = validated_data.pop('is_active')
            user.is_active = is_active
            instance.is_active = is_active
        user.save()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.updated_by = request.user
        instance.save()
        return instance


class BaseUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    phone_number = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def _school_from_request(self):
        return None


class AdminUserCreateSerializer(BaseUserCreateSerializer):
    def create(self, validated_data):
        raise serializers.ValidationError(
            'Admins cannot create users. Users must register themselves.'
        )


class TeacherCreateSerializer(BaseUserCreateSerializer):
    gender = serializers.ChoiceField(choices=Teacher.Gender.choices)
    phone = serializers.CharField(required=False, allow_blank=True, default='')

    def create(self, validated_data):
        raise serializers.ValidationError(
            'Admins cannot create users. Teachers must register themselves.'
        )


class StudentCreateSerializer(BaseUserCreateSerializer):
    gender = serializers.ChoiceField(choices=Student.Gender.choices)
    date_of_birth = serializers.DateField(required=False, allow_null=True, default=None)
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    parent_name = serializers.CharField(required=False, allow_blank=True, default='')
    parent_phone = serializers.CharField(required=False, allow_blank=True, default='')
    address = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def create(self, validated_data):
        raise serializers.ValidationError(
            'Admins cannot create users. Students must register themselves.'
        )
