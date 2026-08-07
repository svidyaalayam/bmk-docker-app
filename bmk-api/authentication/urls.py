from django.urls import path

from .views import (
    AdminDashboardView,
    LoginView,
    MeView,
    RefreshView,
    StudentDashboardView,
    TeacherDashboardView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', RefreshView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='dashboard-teacher'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='dashboard-student'),
]
