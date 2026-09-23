from django.db import migrations, models


def collapse_school_settings(apps, schema_editor):
    School = apps.get_model('school', 'School')
    SchoolSettings = apps.get_model('school', 'SchoolSettings')

    active_school = School.objects.filter(is_active=True).order_by('id').first()
    target = SchoolSettings.objects.order_by('id').first()
    if target is None:
        if active_school is None:
            return
        target = SchoolSettings.objects.create(
            school_id=active_school.id,
            school_slug='school',
            school_number=1,
            lesson_app='sikshavahini',
            school_name='Online School',
        )

    if active_school is not None:
        source = SchoolSettings.objects.filter(school_id=active_school.id).first()
        target.school_slug = active_school.slug
        target.school_number = active_school.school_number
        target.lesson_app = active_school.lesson_app
        if source is not None and source.pk != target.pk:
            for field in (
                'school_name',
                'logo',
                'tagline',
                'introduction',
                'secondary_language',
                'introduction_secondary',
                'footer_text',
            ):
                setattr(target, field, getattr(source, field))
    target.save()
    SchoolSettings.objects.exclude(pk=target.pk).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0017_remove_profile_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolsettings',
            name='school_slug',
            field=models.CharField(default='school', max_length=100),
        ),
        migrations.AddField(
            model_name='schoolsettings',
            name='school_number',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='schoolsettings',
            name='lesson_app',
            field=models.CharField(
                choices=[
                    ('sikshavahini', 'Sikshavahini'),
                    ('sunaadam', 'Sunaadam'),
                ],
                default='sikshavahini',
                max_length=20,
            ),
        ),
        migrations.RunPython(collapse_school_settings, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='schoolsettings',
            name='school_number',
            field=models.PositiveIntegerField(default=1, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='teachingclass',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='course',
            name='school',
        ),
        migrations.RemoveField(
            model_name='teachingclass',
            name='school',
        ),
        migrations.RemoveField(
            model_name='adminrequest',
            name='school',
        ),
        migrations.RemoveField(
            model_name='studentteacherrequest',
            name='school',
        ),
        migrations.RemoveField(
            model_name='schoolsettings',
            name='school',
        ),
        migrations.DeleteModel(
            name='School',
        ),
    ]
