from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from school.models import Student, Teacher
from school.tenancy import resolve_school

from .emails import (
    email_token_generator,
    send_confirmation_email,
    send_password_reset_email,
    user_from_uid,
)
from .usernames import username_for_school_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    school_id = serializers.SerializerMethodField()
    school_slug = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    lesson_app = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone_number',
            'school_id',
            'school_slug',
            'school_name',
            'lesson_app',
            'email_verified',
            'is_active',
            'profile_locked',
            'legacy_uid',
            'date_joined',
            'last_login',
            'avatar_url',
        )
        read_only_fields = fields

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None
        # Relative /media/... path works with Vite/Nginx proxies.
        return obj.avatar.url

    @staticmethod
    def _deployment_school():
        from school.tenancy import resolve_school

        return resolve_school(required=False)

    def get_school_id(self, obj):
        school = self._deployment_school()
        return school.id if school else None

    def get_school_slug(self, obj):
        school = self._deployment_school()
        return school.school_slug if school else None

    def get_school_name(self, obj):
        school = self._deployment_school()
        return school.school_name if school else None

    def get_lesson_app(self, obj):
        school = self._deployment_school()
        return school.lesson_app if school else 'sikshavahini'


class ProfileUpdateSerializer(serializers.Serializer):
    """Users may update display details only — not username or email."""

    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=15)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'phone_number':
                setattr(instance, field, value or None)
            else:
                setattr(instance, field, value)
        instance.save(update_fields=[*validated_data.keys()])
        return instance


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

    def validate_avatar(self, value):
        from django.conf import settings

        max_bytes = getattr(settings, 'MAX_AVATAR_BYTES', 100 * 1024)
        if value.size > max_bytes:
            kb = max_bytes // 1024
            raise serializers.ValidationError(f'Avatar must be {kb} KB or smaller.')
        content_type = getattr(value, 'content_type', '') or ''
        allowed = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
        if content_type and content_type not in allowed:
            raise serializers.ValidationError('Use a JPEG, PNG, WebP, or GIF image.')
        return value

    def update(self, instance, validated_data):
        if instance.avatar:
            instance.avatar.delete(save=False)
        instance.avatar = validated_data['avatar']
        instance.save(update_fields=['avatar'])
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login using email (or username) + password for this school."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False
        self.fields['email'] = serializers.EmailField(required=False, write_only=True)

    def validate(self, attrs):
        request = self.context.get('request')
        raw_login = (
            (attrs.get(self.username_field) or '')
            or (request.data.get('email') if request is not None else '')
            or ''
        )
        raw_login = str(raw_login).strip()
        password = attrs.get('password') or ''

        school = resolve_school(request, required=False) if request is not None else None
        users = User.objects.all()
        user = None
        if raw_login:
            if '@' in raw_login:
                # Users enter their normal email. The school supplies the
                # permanent UUID suffix used by the private Django username.
                if school is not None:
                    user = users.filter(
                        username__iexact=username_for_school_email(raw_login, school)
                    ).first()
                # Supports older accounts until their usernames are migrated.
                if user is None:
                    user = users.filter(email__iexact=raw_login.lower()).first()
            if user is None:
                user = users.filter(username__iexact=raw_login).first()
            if user is None and '@' not in raw_login:
                user = users.filter(email__iexact=raw_login.lower()).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                {'detail': 'Invalid email or password.'},
                code='authorization',
            )

        if not user.email_verified and not user.is_superuser:
            raise serializers.ValidationError(
                {'detail': 'Please confirm your email before signing in.'},
                code='authorization',
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {
                    'detail': (
                        'Your email is confirmed. A school admin must activate '
                        'your account before you can sign in.'
                    )
                },
                code='authorization',
            )
        if not request or request.data.get('terms_accepted') is not True:
            raise serializers.ValidationError(
                {'detail': 'You must accept the Terms & Conditions before signing in.'},
                code='authorization',
            )

        self.user = user
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user, context=self.context).data,
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email or ''
        school = resolve_school(required=False)
        token['school_id'] = school.id if school else None
        token['school_slug'] = school.school_slug if school else None
        token['lesson_app'] = school.lesson_app if school else 'sikshavahini'
        # Teaching-class ids for lesson-application view permissions
        try:
            from school.class_views import _classes_for_user

            token['class_ids'] = list(
                _classes_for_user(user).values_list('id', flat=True)
            )
        except Exception:
            token['class_ids'] = []
        return token


class StudentRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    parent_name = serializers.CharField(max_length=100)
    gender = serializers.ChoiceField(choices=Student.Gender.choices)
    date_of_birth = serializers.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    phone = serializers.CharField(max_length=20)

    def validate_email(self, value):
        email = value.strip().lower()
        if len(email) > 150:
            raise serializers.ValidationError('Email must be 150 characters or fewer.')
        school = resolve_school(self.context['request'], required=True)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return email

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        school = resolve_school(request, required=True)
        password = validated_data.pop('password')
        email = validated_data['email']
        phone = validated_data['phone']

        user = User(
            username=username_for_school_email(email, school),
            email=email,
            first_name=validated_data['first_name'].strip(),
            last_name=validated_data['last_name'].strip(),
            role=User.Roles.STUDENT,
            phone_number=phone,
            is_active=False,
            email_verified=False,
            profile_locked=True,
        )
        user.set_password(password)
        user.save()

        Student.objects.create(
            user=user,
            gender=validated_data['gender'],
            date_of_birth=validated_data['date_of_birth'],
            phone=phone,
            parent_name=validated_data['parent_name'].strip(),
        )
        send_confirmation_email(user, request)
        return user


class TeacherRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    gender = serializers.ChoiceField(choices=Teacher.Gender.choices)
    phone = serializers.CharField(max_length=20)

    def validate_email(self, value):
        email = value.strip().lower()
        if len(email) > 150:
            raise serializers.ValidationError('Email must be 150 characters or fewer.')
        school = resolve_school(self.context['request'], required=True)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return email

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        school = resolve_school(request, required=True)
        password = validated_data.pop('password')
        email = validated_data['email']
        phone = validated_data['phone']

        user = User(
            username=username_for_school_email(email, school),
            email=email,
            first_name=validated_data['first_name'].strip(),
            last_name=validated_data['last_name'].strip(),
            role=User.Roles.TEACHER,
            phone_number=phone,
            is_active=False,
            email_verified=False,
            profile_locked=True,
        )
        user.set_password(password)
        user.save()

        Teacher.objects.create(
            user=user,
            gender=validated_data['gender'],
            phone=phone,
        )
        send_confirmation_email(user, request)
        return user


class ConfirmEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def save(self, **kwargs):
        user = user_from_uid(self.validated_data['uid'])
        token = self.validated_data['token']
        if user is None or not email_token_generator.check_token(user, token):
            raise serializers.ValidationError({'detail': 'Invalid or expired confirmation link.'})
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, **kwargs):
        request = self.context.get('request')
        email = self.validated_data['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        # Always succeed to avoid email enumeration
        if user is not None and user.email:
            send_password_reset_email(user, request)
        return None


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def save(self, **kwargs):
        user = user_from_uid(self.validated_data['uid'])
        token = self.validated_data['token']
        if user is None or not email_token_generator.check_token(user, token):
            raise serializers.ValidationError({'detail': 'Invalid or expired reset link.'})
        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])
        return user
