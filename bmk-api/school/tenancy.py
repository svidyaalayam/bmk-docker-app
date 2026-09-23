from rest_framework.exceptions import NotFound

from .models import SchoolSettings


def resolve_school(request=None, required=True):
    """
    Return the singleton settings record for this deployment.

    The function name is retained temporarily for API compatibility while
    the old School model is removed.
    """
    school = SchoolSettings.objects.order_by('id').first()
    if school:
        return school
    if required:
        raise NotFound('School is not configured for this deployment.')
    return None
