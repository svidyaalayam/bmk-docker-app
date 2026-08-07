from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow only users with ADMIN role (or Django superuser)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == user.Roles.ADMIN or user.is_superuser)
        )


class IsTeacherRole(BasePermission):
    """Allow TEACHER or ADMIN roles."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role in (user.Roles.TEACHER, user.Roles.ADMIN)
        )


class IsStudentRole(BasePermission):
    """Allow STUDENT role only."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == user.Roles.STUDENT
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner may read/write; admin may always access."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == user.Roles.ADMIN or user.is_superuser:
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        return owner == user
