"""Class-catalog endpoints consumed by the lesson applications."""

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SchoolSettings, TeachingClass


class HasSikshavahiniServiceKey(permissions.BasePermission):
    def has_permission(self, request, view):
        expected = (getattr(settings, 'SIKSHAVAHINI_SHARED_SECRET', '') or '').strip()
        if not expected:
            return False
        provided = (
            request.headers.get('X-Sikshavahini-Key')
            or request.META.get('HTTP_X_SIKSHAVAHINI_KEY')
            or ''
        ).strip()
        return provided == expected


class HasSunaadamServiceKey(permissions.BasePermission):
    def has_permission(self, request, view):
        expected = (getattr(settings, 'SUNAADAM_SHARED_SECRET', '') or '').strip()
        if not expected:
            return False
        provided = (
            request.headers.get('X-Sunaadam-Key')
            or request.META.get('HTTP_X_SUNAADAM_KEY')
            or ''
        ).strip()
        return provided == expected


class SikshavahiniClassCatalogView(APIView):
    """
    GET /api/sikshavahini/classes/?school=<slug>
    Returns teaching classes for Sikshavahini permission assignment.
    """

    authentication_classes = []
    permission_classes = [HasSikshavahiniServiceKey]

    def get(self, request):
        settings = SchoolSettings.objects.first()
        qs = TeachingClass.objects.filter(is_active=True)
        data = [
            {
                'id': tc.id,
                'name': tc.name,
                'school_slug': settings.school_slug if settings else '',
                'school_name': settings.school_name if settings else '',
                'description': tc.description or '',
            }
            for tc in qs.order_by('name')
        ]
        return Response({'classes': data})


class SikshavahiniSchoolsCatalogView(APIView):
    """GET /api/sikshavahini/schools/ — active schools for filtering."""

    authentication_classes = []
    permission_classes = [HasSikshavahiniServiceKey]

    def get(self, request):
        settings = SchoolSettings.objects.first()
        return Response(
            {
                'schools': (
                    [{'id': settings.id, 'name': settings.school_name, 'slug': settings.school_slug}]
                    if settings else []
                )
            }
        )


class SunaadamClassCatalogView(APIView):
    """Return classes belonging to schools configured for Sunaadam."""

    authentication_classes = []
    permission_classes = [HasSunaadamServiceKey]

    def get(self, request):
        settings = SchoolSettings.objects.first()
        qs = TeachingClass.objects.filter(
            is_active=True,
        )
        if settings and settings.lesson_app != SchoolSettings.LessonApp.SUNAADAM:
            qs = qs.none()
        data = [
            {
                'id': tc.id,
                'name': tc.name,
                'school_slug': settings.school_slug if settings else '',
                'school_name': settings.school_name if settings else '',
                'description': tc.description or '',
            }
            for tc in qs.order_by('name')
        ]
        return Response({'classes': data})


class SunaadamSchoolsCatalogView(APIView):
    """Return active schools configured to use Sunaadam."""

    authentication_classes = []
    permission_classes = [HasSunaadamServiceKey]

    def get(self, request):
        settings = SchoolSettings.objects.first()
        return Response(
            {
                'schools': (
                    [{'id': settings.id, 'name': settings.school_name, 'slug': settings.school_slug}]
                    if settings and settings.lesson_app == SchoolSettings.LessonApp.SUNAADAM
                    else []
                )
            }
        )
