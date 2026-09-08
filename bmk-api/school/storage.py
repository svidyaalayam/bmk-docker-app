"""Storage backends for session homework / materials (local or Azure Blob)."""

from __future__ import annotations

import re
import uuid
from pathlib import PurePosixPath

from django.conf import settings
from django.core.files.storage import FileSystemStorage, storages


def homework_storage_backend_name() -> str:
    backend = getattr(settings, 'HOMEWORK_STORAGE_BACKEND', 'local').strip().lower()
    if backend == 'azure_blob' and 'azure_homework' in getattr(settings, 'STORAGES', {}):
        return 'azure_blob'
    return 'local'


def select_homework_storage():
    """Callable storage for FileField — Azure when configured, else local media."""
    if homework_storage_backend_name() == 'azure_blob':
        return storages['azure_homework']
    return storages['default'] if 'default' in getattr(settings, 'STORAGES', {}) else FileSystemStorage()


def _safe_filename(filename: str) -> str:
    name = PurePosixPath(filename or 'file').name
    name = re.sub(r'[^\w.\-]+', '_', name).strip('._') or 'file'
    return name[:180]


def student_homework_upload_to(instance, filename: str) -> str:
    school_slug = instance.session.teaching_class.school.slug
    class_id = instance.session.teaching_class_id
    session_id = instance.session_id
    student_id = instance.student_id
    return (
        f'{school_slug}/classes/{class_id}/sessions/{session_id}/'
        f'homework/{student_id}/{uuid.uuid4().hex}_{_safe_filename(filename)}'
    )


def session_material_upload_to(instance, filename: str) -> str:
    school_slug = instance.session.teaching_class.school.slug
    class_id = instance.session.teaching_class_id
    session_id = instance.session_id
    kind = (instance.kind or 'material').lower()
    return (
        f'{school_slug}/classes/{class_id}/sessions/{session_id}/'
        f'materials/{kind}/{uuid.uuid4().hex}_{_safe_filename(filename)}'
    )


def apply_storage_metadata(instance) -> None:
    """Set storage_backend + storage_uri after a file is saved."""
    backend = homework_storage_backend_name()
    instance.storage_backend = backend
    if instance.file:
        # Persist stable blob/object name — never a time-limited SAS URL.
        instance.storage_uri = instance.file.name or ''
    else:
        instance.storage_uri = ''
    instance.save(update_fields=['storage_backend', 'storage_uri', 'updated_at'])


def file_access_url(instance) -> str | None:
    """Public access URL for a homework/material file (SAS when Azure private)."""
    if instance.file:
        try:
            return instance.file.url
        except Exception:
            pass
    return getattr(instance, 'storage_uri', None) or None


def delete_stored_file(instance) -> None:
    if not instance.file:
        return
    try:
        instance.file.delete(save=False)
    except Exception:
        # Blob may already be gone; still allow DB row deletion.
        pass
