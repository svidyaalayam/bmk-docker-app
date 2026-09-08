from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError

from .models import School


def _slug_from_host(host: str) -> str:
    """
    uk.telugu.localhost / balavikas.x.x.x.x.nip.io → uk.telugu / balavikas
    Multi-label prefixes are allowed (type/region nesting).
    """
    from django.conf import settings

    hostname = (host or '').split(':')[0].strip().lower()
    if not hostname or hostname in {'localhost', '127.0.0.1'}:
        return ''

    app_domain = getattr(settings, 'APP_DOMAIN', 'localhost').strip().lower()
    candidates = []
    if app_domain:
        candidates.append(app_domain)
    if 'localhost' not in candidates:
        candidates.append('localhost')

    for domain in candidates:
        suffix = f'.{domain}'
        if hostname == domain:
            return ''
        if hostname.endswith(suffix):
            sub = hostname[: -len(suffix)]
            if sub:
                return sub
    return ''


def resolve_school(request, required=True):
    """
    Resolve tenant school from:
    1) ?school=<slug> query param
    2) X-School-Slug header
    3) Host subdomain prefix (uk.telugu.localhost)
    4) School.domain match
    5) request.user.school for authenticated users
    """
    slug = (
        request.query_params.get('school')
        or request.headers.get('X-School-Slug')
        or ''
    ).strip().lower()

    if not slug:
        slug = _slug_from_host(request.get_host())

    if slug:
        try:
            return School.objects.get(slug=slug, is_active=True)
        except School.DoesNotExist as exc:
            raise NotFound('School not found.') from exc

    host = request.get_host().split(':')[0].strip().lower()
    if host and host not in {'localhost', '127.0.0.1'}:
        school = School.objects.filter(domain__iexact=host, is_active=True).first()
        if school:
            return school

    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and user.school_id:
        return user.school

    if required:
        raise ValidationError(
            {
                'school': (
                    'School slug is required (?school=... or X-School-Slug '
                    'or school subdomain host).'
                )
            }
        )
    return None


def get_school_or_404(slug: str) -> School:
    return get_object_or_404(School, slug=slug, is_active=True)
