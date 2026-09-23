from django.db import migrations


def normalize_users_and_profiles(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    Student = apps.get_model('school', 'Student')
    Teacher = apps.get_model('school', 'Teacher')

    for user in User.objects.all().iterator():
        email = (user.email or '').strip().lower()
        if email and not user.is_superuser and user.username != email:
            if not User.objects.filter(username=email).exclude(pk=user.pk).exists():
                user.username = email
                user.save(update_fields=['username'])

        if user.is_superuser:
            continue
        if user.role == 'STUDENT':
            Student.objects.get_or_create(
                user_id=user.pk,
                defaults={'gender': 'M', 'is_active': user.is_active},
            )
        elif user.role == 'TEACHER':
            Teacher.objects.get_or_create(
                user_id=user.pk,
                defaults={'gender': 'M', 'is_active': user.is_active},
            )


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0007_remove_user_school'),
        ('school', '0018_remove_school_model'),
    ]

    operations = [
        migrations.RunPython(normalize_users_and_profiles, migrations.RunPython.noop),
    ]
