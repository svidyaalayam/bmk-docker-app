import hashlib
import uuid

from django.db import migrations, models


def update_school_usernames(apps, schema_editor):
    School = apps.get_model('school', 'School')
    User = apps.get_model('authentication', 'User')
    for school in School.objects.all().iterator():
        if school.user_identifier is None:
            school.user_identifier = uuid.uuid4()
            school.save(update_fields=['user_identifier'])
        suffix = f'--{school.user_identifier.hex}'
        for user in User.objects.filter(school_id=school.id).iterator():
            email = (user.email or '').strip().lower()
            if not email:
                # School accounts are email-based; retain an exceptional blank-email
                # username rather than risking a collision during this migration.
                continue
            local, separator, domain = email.partition('@')
            if not separator:
                username = f'{email[:150 - len(suffix)]}{suffix}'
            else:
                available_local_length = 150 - len(suffix) - len(separator) - len(domain)
                if available_local_length < len(local):
                    digest = hashlib.sha256(email.encode()).hexdigest()[:10]
                    local = f'{local[:max(1, available_local_length - len(digest) - 1)]}-{digest}'
                username = f'{local}{suffix}{separator}{domain}'
            user.username = username
            user.save(update_fields=['username'])


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_alter_user_legacy_uid'),
        ('school', '0011_student_teacher_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='user_identifier',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
        migrations.RunPython(update_school_usernames, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='school',
            name='user_identifier',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
