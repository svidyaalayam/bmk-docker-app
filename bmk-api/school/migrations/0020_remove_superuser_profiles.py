from django.db import migrations


def remove_superuser_profiles(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    Student = apps.get_model('school', 'Student')
    Teacher = apps.get_model('school', 'Teacher')
    superuser_ids = User.objects.filter(is_superuser=True).values_list('id', flat=True)
    Student.objects.filter(user_id__in=superuser_ids).delete()
    Teacher.objects.filter(user_id__in=superuser_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0019_normalize_usernames_and_profiles'),
    ]

    operations = [
        migrations.RunPython(remove_superuser_profiles, migrations.RunPython.noop),
    ]
