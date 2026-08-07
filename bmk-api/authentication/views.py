from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsAdminRole, IsStudentRole, IsTeacherRole
from .serializers import CustomTokenObtainPairSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — username + password → JWT + user profile."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    """POST /api/auth/refresh/ — exchange refresh token for a new access token."""

    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """GET /api/auth/me/ — current authenticated user profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminDashboardView(APIView):
    """Sample admin-only endpoint used to verify role guardrails."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response({
            'dashboard': 'admin',
            'message': f'Welcome Admin {request.user.username}',
            'capabilities': [
                'Grant admission logs',
                'Manage users and roles',
                'Create admins, teachers, and students',
                'Override system access',
            ],
        })


class TeacherDashboardView(APIView):
    """Sample teacher-only endpoint used to verify role guardrails."""

    permission_classes = [IsTeacherRole]

    def get(self, request):
        return Response({
            'dashboard': 'teacher',
            'message': f'Welcome Teacher {request.user.username}',
            'capabilities': [
                'View assigned classes',
                'Enter grades',
                'Track attendance',
            ],
        })


class StudentDashboardView(APIView):
    """Sample student-only endpoint used to verify role guardrails."""

    permission_classes = [IsStudentRole]

    def get(self, request):
        return Response({
            'dashboard': 'student',
            'message': f'Welcome Student {request.user.username}',
            'capabilities': [
                'View assigned lessons',
                'Submit homework',
                'Access personal grades',
            ],
        })
