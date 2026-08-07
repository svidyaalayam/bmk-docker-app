from django.urls import path

from .views import (
    AdminUserCreateView,
    HomepageContentView,
    SchoolListView,
    SchoolSettingsPublicView,
    StudentListCreateView,
    TeacherListCreateView,
    UserListView,
)

urlpatterns = [
    path('public/schools/', SchoolListView.as_view(), name='public-schools'),
    path('public/homepage/', HomepageContentView.as_view(), name='public-homepage'),
    path('public/school/', SchoolSettingsPublicView.as_view(), name='public-school-settings'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/admins/', AdminUserCreateView.as_view(), name='admin-user-create'),
    path('teachers/', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
]
