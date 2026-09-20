import hashlib

from django.db import migrations, models


def assign_school_numbers_and_update_usernames(apps, schema_editor):
    School = apps.get_model('school', 'School')
    User = apps.get_model('authentication', 'User')
    schools = list(School.objects.all())
    # Preserve the requested number for Balamukundam, including its newer Telugu slug.
    schools.sort(key=lambda school: (school.slug not in {'balamukundam', 'uk.telugu'}, school.id))
    for number, school in enumerate(schools, start=1):
        school.school_number = number
        school.save(update_fields=['school_number'])

    # A desired short name may already be held by another school account that is
    # also being renamed. Move every email-based tenant account aside first so
    # username uniqueness cannot depend on the order in which schools are visited.
    tenant_users = User.objects.exclude(school_id__isnull=True).exclude(email='')
    for user in tenant_users.iterator():
        user.username = f'__school-number-migration-{user.pk}'
        user.save(update_fields=['username'])

    for school in schools:
        number = school.school_number
        suffix = f'--{number}'
        for user in User.objects.filter(school_id=school.id).order_by('id').iterator():
            email = (user.email or '').strip().lower()
            if not email:
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
            # Bad historical seed data can contain the same email more than once
            # in one school. Keep every row without blocking deployment; the first
            # account retains the normal email-based username and later duplicates
            # receive a clearly marked, unique internal identifier.
            candidate = username
            if User.objects.filter(username__iexact=candidate).exclude(pk=user.pk).exists():
                duplicate_marker = f'-duplicate-{user.pk}'
                if separator:
                    available_local_length = 150 - len(duplicate_marker) - len(suffix) - len(separator) - len(domain)
                    candidate = f'{local[:max(1, available_local_length)]}{duplicate_marker}{suffix}{separator}{domain}'
                else:
                    candidate = f'{email[:150 - len(duplicate_marker) - len(suffix)]}{duplicate_marker}{suffix}'
            user.username = candidate
            user.save(update_fields=['username'])


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0012_school_user_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='school_number',
            field=models.PositiveIntegerField(editable=False, null=True, unique=True),
        ),
        migrations.RunPython(assign_school_numbers_and_update_usernames, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='school',
            name='school_number',
            field=models.PositiveIntegerField(editable=False, unique=True),
        ),
    ]
