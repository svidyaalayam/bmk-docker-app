from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source='school.id', read_only=True, allow_null=True)
    school_slug = serializers.CharField(source='school.slug', read_only=True, allow_null=True)
    school_name = serializers.CharField(source='school.name', read_only=True, allow_null=True)

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
        )
        read_only_fields = fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login that scopes users to a school when ?school= / X-School-Slug is provided."""

    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get('request')
        school_slug = ''
        if request is not None:
            query_params = getattr(request, 'query_params', None)
            if query_params is not None:
                school_slug = query_params.get('school') or ''
            if not school_slug:
                school_slug = (
                    request.headers.get('X-School-Slug')
                    or request.META.get('HTTP_X_SCHOOL_SLUG')
                    or ''
                )
            school_slug = school_slug.strip().lower()

        if school_slug:
            if not self.user.school_id or self.user.school.slug != school_slug:
                raise serializers.ValidationError(
                    {'detail': 'Invalid credentials for this school.'},
                    code='authorization',
                )

        data['user'] = UserSerializer(self.user).data
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['school_id'] = user.school_id
        token['school_slug'] = user.school.slug if user.school_id else None
        return token
