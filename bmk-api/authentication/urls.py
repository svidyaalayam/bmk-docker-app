from django.urls import path

from .views import (
    ActivateUserView,
    AdminDashboardView,
    AvatarUploadView,
    ConfirmEmailView,
    DeactivateUserView,
    LoginView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PendingUsersView,
    RefreshView,
    ResendConfirmationView,
    StudentDashboardView,
    StudentRegisterView,
    TeacherDashboardView,
    TeacherRegisterView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', RefreshView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('me/avatar/', AvatarUploadView.as_view(), name='auth-me-avatar'),
    path('register/student/', StudentRegisterView.as_view(), name='auth-register-student'),
    path('register/teacher/', TeacherRegisterView.as_view(), name='auth-register-teacher'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='auth-confirm-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path(
        'password-reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='auth-password-reset-confirm',
    ),
    path('resend-confirmation/', ResendConfirmationView.as_view(), name='auth-resend-confirmation'),
    path('pending-users/', PendingUsersView.as_view(), name='auth-pending-users'),
    path('users/<int:user_id>/activate/', ActivateUserView.as_view(), name='auth-activate-user'),
    path(
        'users/<int:user_id>/deactivate/',
        DeactivateUserView.as_view(),
        name='auth-deactivate-user',
    ),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='dashboard-teacher'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='dashboard-student'),
]
