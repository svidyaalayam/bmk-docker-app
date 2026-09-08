from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from authentication.serializers import UserSerializer
from .models import Course, CourseClass, School, SchoolSettings, SchoolSubtype, SchoolType, Student, Teacher

User = get_user_model()


class SchoolSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    type_slug = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    subtype_slug = serializers.SerializerMethodField()
    subtype_name = serializers.SerializerMethodField()
    type_display_order = serializers.SerializerMethodField()
    subtype_display_order = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = (
            'id',
            'name',
            'slug',
            'domain',
            'logo_url',
            'type_slug',
            'type_name',
            'type_display_order',
            'subtype_slug',
            'subtype_name',
            'subtype_display_order',
        )

    def get_logo_url(self, obj):
        settings = getattr(obj, 'settings', None)
        if not settings or not settings.logo:
            return None
        return settings.logo.url

    def get_type_slug(self, obj):
        if obj.subtype_id and obj.subtype:
            return obj.subtype.school_type.slug
        return None

    def get_type_name(self, obj):
        if obj.subtype_id and obj.subtype:
            return obj.subtype.school_type.name
        return None

    def get_type_display_order(self, obj):
        if obj.subtype_id and obj.subtype:
            return obj.subtype.school_type.display_order
        return 999

    def get_subtype_slug(self, obj):
        return obj.subtype.slug if obj.subtype_id and obj.subtype else None

    def get_subtype_name(self, obj):
        return obj.subtype.name if obj.subtype_id and obj.subtype else None

    def get_subtype_display_order(self, obj):
        return obj.subtype.display_order if obj.subtype_id and obj.subtype else 999


class SchoolCatalogSchoolSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = ('id', 'name', 'slug', 'domain', 'logo_url')

    def get_logo_url(self, obj):
        settings = getattr(obj, 'settings', None)
        if not settings or not settings.logo:
            return None
        return settings.logo.url


class SchoolCatalogSubtypeSerializer(serializers.ModelSerializer):
    schools = SchoolCatalogSchoolSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolSubtype
        fields = ('id', 'name', 'slug', 'display_order', 'schools')


class SchoolCatalogSerializer(serializers.ModelSerializer):
    subtypes = SchoolCatalogSubtypeSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolType
        fields = ('id', 'name', 'slug', 'display_order', 'subtypes')


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


class SchoolSettingsSerializer(serializers.ModelSerializer):
    school_slug = serializers.CharField(source='school.slug', read_only=True)
    school_id = serializers.IntegerField(source='school.id', read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolSettings
        fields = (
            'school_id',
            'school_slug',
            'school_name',
            'logo_url',
            'tagline',
            'introduction',
            'secondary_language',
            'introduction_secondary',
            'footer_text',
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


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

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
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'user', 'is_active', 'created_at', 'updated_at')


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

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
        request = self.context['request']
        school = getattr(request.user, 'school', None)
        if school is None:
            raise serializers.ValidationError('Admin user is not linked to a school.')
        return school


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
