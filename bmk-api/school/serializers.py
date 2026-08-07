from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from authentication.serializers import UserSerializer
from .models import Course, CourseClass, School, SchoolSettings, Student, Teacher

User = get_user_model()


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('id', 'name', 'slug', 'domain')


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

    class Meta:
        model = SchoolSettings
        fields = (
            'school_id',
            'school_slug',
            'school_name',
            'tagline',
            'introduction',
            'secondary_language',
            'introduction_secondary',
            'footer_text',
            'updated_at',
        )


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
        password = validated_data.pop('password')
        school = self._school_from_request()
        user = User(
            role=User.Roles.ADMIN,
            is_staff=True,
            school=school,
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user


class TeacherCreateSerializer(BaseUserCreateSerializer):
    gender = serializers.ChoiceField(choices=Teacher.Gender.choices)
    phone = serializers.CharField(required=False, allow_blank=True, default='')

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        school = self._school_from_request()
        password = validated_data.pop('password')
        gender = validated_data.pop('gender')
        phone = validated_data.pop('phone', '')
        phone_number = validated_data.pop('phone_number', '') or phone

        user = User(
            role=User.Roles.TEACHER,
            phone_number=phone_number or None,
            school=school,
            **validated_data,
        )
        user.set_password(password)
        user.save()

        return Teacher.objects.create(
            school=school,
            user=user,
            gender=gender,
            phone=phone or phone_number,
            created_by=request.user,
            updated_by=request.user,
        )


class StudentCreateSerializer(BaseUserCreateSerializer):
    gender = serializers.ChoiceField(choices=Student.Gender.choices)
    date_of_birth = serializers.DateField(required=False, allow_null=True, default=None)
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    parent_name = serializers.CharField(required=False, allow_blank=True, default='')
    parent_phone = serializers.CharField(required=False, allow_blank=True, default='')
    address = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        school = self._school_from_request()
        password = validated_data.pop('password')
        profile_fields = {
            'gender': validated_data.pop('gender'),
            'date_of_birth': validated_data.pop('date_of_birth', None),
            'phone': validated_data.pop('phone', ''),
            'parent_name': validated_data.pop('parent_name', ''),
            'parent_phone': validated_data.pop('parent_phone', ''),
            'address': validated_data.pop('address', ''),
            'notes': validated_data.pop('notes', ''),
        }
        phone_number = validated_data.pop('phone_number', '') or profile_fields['phone']

        user = User(
            role=User.Roles.STUDENT,
            phone_number=phone_number or None,
            school=school,
            **validated_data,
        )
        user.set_password(password)
        user.save()

        return Student.objects.create(
            school=school,
            user=user,
            created_by=request.user,
            updated_by=request.user,
            **profile_fields,
        )
