"""Class-catalog endpoints consumed by the lesson applications."""

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import School, TeachingClass


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
        school_slug = (request.query_params.get('school') or '').strip().lower()
        qs = TeachingClass.objects.filter(is_active=True).select_related('school')
        if school_slug:
            qs = qs.filter(school__slug=school_slug)
        data = [
            {
                'id': tc.id,
                'name': tc.name,
                'school_slug': tc.school.slug,
                'school_name': tc.school.name,
                'description': tc.description or '',
            }
            for tc in qs.order_by('school__name', 'name')
        ]
        return Response({'classes': data})


class SikshavahiniSchoolsCatalogView(APIView):
    """GET /api/sikshavahini/schools/ — active schools for filtering."""

    authentication_classes = []
    permission_classes = [HasSikshavahiniServiceKey]

    def get(self, request):
        schools = School.objects.filter(is_active=True).order_by('name')
        return Response(
            {
                'schools': [
                    {'id': s.id, 'name': s.name, 'slug': s.slug} for s in schools
                ]
            }
        )


class SunaadamClassCatalogView(APIView):
    """Return classes belonging to schools configured for Sunaadam."""

    authentication_classes = []
    permission_classes = [HasSunaadamServiceKey]

    def get(self, request):
        school_slug = (request.query_params.get('school') or '').strip().lower()
        qs = TeachingClass.objects.filter(
            is_active=True,
            school__lesson_app=School.LessonApp.SUNAADAM,
        ).select_related('school')
        if school_slug:
            qs = qs.filter(school__slug=school_slug)
        data = [
            {
                'id': tc.id,
                'name': tc.name,
                'school_slug': tc.school.slug,
                'school_name': tc.school.name,
                'description': tc.description or '',
            }
            for tc in qs.order_by('school__name', 'name')
        ]
        return Response({'classes': data})


class SunaadamSchoolsCatalogView(APIView):
    """Return active schools configured to use Sunaadam."""

    authentication_classes = []
    permission_classes = [HasSunaadamServiceKey]

    def get(self, request):
        schools = School.objects.filter(
            is_active=True,
            lesson_app=School.LessonApp.SUNAADAM,
        ).order_by('name')
        return Response(
            {
                'schools': [
                    {'id': s.id, 'name': s.name, 'slug': s.slug} for s in schools
                ]
            }
        )
