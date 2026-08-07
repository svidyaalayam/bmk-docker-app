from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdminRole
from authentication.serializers import UserSerializer
from .models import Course, CourseClass, School, Student, Teacher
from .serializers import (
    AdminUserCreateSerializer,
    HomepageContentSerializer,
    SchoolSerializer,
    SchoolSettingsSerializer,
    StudentCreateSerializer,
    StudentSerializer,
    TeacherCreateSerializer,
    TeacherSerializer,
)
from .tenancy import resolve_school

User = get_user_model()


class SchoolListView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        schools = School.objects.filter(is_active=True)
        return Response(SchoolSerializer(schools, many=True).data)


class HomepageContentView(APIView):
    """Public homepage payload for one school."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        school = resolve_school(request, required=True)
        settings = getattr(school, 'settings', None)
        if settings is None:
            return Response({'detail': 'School settings are not configured.'}, status=404)

        courses = school.courses.filter(is_published=True, is_active=True).prefetch_related(
            Prefetch(
                'classes',
                queryset=CourseClass.objects.filter(is_published=True, is_active=True),
            )
        )
        payload = {
            'school': settings,
            'courses': courses,
        }
        return Response(HomepageContentSerializer(payload).data)


class SchoolSettingsPublicView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        school = resolve_school(request, required=True)
        settings = getattr(school, 'settings', None)
        if settings is None:
            return Response({'detail': 'School settings are not configured.'}, status=404)
        return Response(SchoolSettingsSerializer(settings).data)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        queryset = User.objects.filter(school=self.request.user.school).order_by('role', 'username')
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role.upper())
        return queryset


class AdminUserCreateView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = AdminUserCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class TeacherListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Teacher.objects.filter(school=self.request.user.school).select_related('user')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TeacherCreateSerializer
        return TeacherSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(TeacherSerializer(teacher).data, status=status.HTTP_201_CREATED)


class StudentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Student.objects.filter(school=self.request.user.school).select_related('user')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentCreateSerializer
        return StudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)
