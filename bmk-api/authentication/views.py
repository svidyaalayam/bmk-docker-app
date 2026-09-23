from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.permissions import IsAdminRole, IsStudentRole, IsTeacherRole
from .emails import send_confirmation_email
from .serializers import (
    AvatarUploadSerializer,
    ConfirmEmailSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — email/username + password → JWT + user profile."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — view or update own profile (not username/email)."""

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'put', 'head', 'options']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={'request': request}).data)


class AvatarUploadView(APIView):
    """POST /api/auth/me/avatar/ — upload profile image (max ~100 KB)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.update(request.user, serializer.validated_data)
        return Response(UserSerializer(user, context={'request': request}).data)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=['avatar'])
        return Response(UserSerializer(user, context={'request': request}).data)


class StudentRegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = StudentRegistrationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'detail': (
                    'Registration received. Please check your email to confirm your address. '
                    'After confirmation, a school admin must activate your account before you can sign in. '
                    'Submitted details cannot be changed.'
                )
            },
            status=status.HTTP_201_CREATED,
        )


class TeacherRegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TeacherRegistrationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'detail': (
                    'Registration received. Please check your email to confirm your address. '
                    'After confirmation, a school admin must activate your account before you can sign in. '
                    'Submitted details cannot be changed.'
                )
            },
            status=status.HTTP_201_CREATED,
        )


class ConfirmEmailView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'detail': (
                    'Email confirmed. A school admin must activate your account '
                    'before you can sign in.'
                )
            }
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'If an account exists for that email, a reset link has been sent.'}
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password has been reset. You can sign in when your account is active.'})


class ResendConfirmationView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if user and not user.email_verified:
            send_confirmation_email(user, request)
        return Response({'detail': 'If that account needs confirmation, an email has been sent.'})


class PendingUsersView(APIView):
    """Admin: list users waiting for activation (email confirmed, inactive)."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        users = (
            User.objects.filter(
                email_verified=True,
                is_active=False,
            )
            .exclude(role=User.Roles.ADMIN)
            .order_by('date_joined')
        )
        return Response(UserSerializer(users, many=True).data)


class ActivateUserView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.role == User.Roles.ADMIN:
            return Response({'detail': 'Cannot change admin activation here.'}, status=400)
        if not user.email_verified:
            return Response({'detail': 'User has not confirmed their email yet.'}, status=400)
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response(UserSerializer(user).data)


class DeactivateUserView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.id == request.user.id:
            return Response({'detail': 'You cannot deactivate yourself.'}, status=400)
        if user.role == User.Roles.ADMIN:
            return Response({'detail': 'Cannot deactivate admin here.'}, status=400)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response(UserSerializer(user).data)


class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        pending = User.objects.filter(
            email_verified=True,
            is_active=False,
        ).count()
        return Response(
            {
                'dashboard': 'admin',
                'message': f'Welcome Admin {request.user.email}',
                'pending_activations': pending,
                'capabilities': [
                    'Review and activate registered students and teachers',
                    'Manage users and roles',
                    'Manage teaching classes, teachers, students, and calendars',
                    'Override system access',
                ],
            }
        )


class TeacherDashboardView(APIView):
    permission_classes = [IsTeacherRole]

    def get(self, request):
        return Response(
            {
                'dashboard': 'teacher',
                'message': f'Welcome Teacher {request.user.email}',
                'capabilities': [
                    'View and update assigned classes',
                    'Manage class calendar, classwork, and homework notes',
                    'Start sessions and mark attendance',
                    'Comment on student session records and review homework',
                ],
            }
        )


class StudentDashboardView(APIView):
    permission_classes = [IsStudentRole]

    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        account_blocked = bool(student and student.account_blocked)
        return Response(
            {
                'dashboard': 'student',
                'message': (
                    'Your account is blocked. Please request activation from the Admin team.'
                    if account_blocked
                    else f'Welcome Student {request.user.email}'
                ),
                'account_blocked': account_blocked,
                'block_reason': student.block_reason if account_blocked else '',
                'capabilities': [
                    'View your classes and calendar',
                    'Add comments on your session records',
                    'Upload homework files and read teacher feedback',
                ],
            }
        )
