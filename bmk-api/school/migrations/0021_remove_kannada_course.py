from django.db import migrations


def remove_kannada_course(apps, schema_editor):
    Course = apps.get_model('school', 'Course')
    Course.objects.filter(title__iexact='Kannada').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0020_remove_superuser_profiles'),
    ]

    operations = [
        migrations.RunPython(
            remove_kannada_course,
            migrations.RunPython.noop,
        ),
    ]
