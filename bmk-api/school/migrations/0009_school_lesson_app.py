from django.db import migrations, models


def assign_music_schools(apps, schema_editor):
    School = apps.get_model('school', 'School')
    School.objects.filter(
        subtype__slug__in=('carnatic-music', 'hindustani-music')
    ).update(lesson_app='sunaadam')


def restore_sikshavahini(apps, schema_editor):
    School = apps.get_model('school', 'School')
    School.objects.filter(lesson_app='sunaadam').update(
        lesson_app='sikshavahini'
    )


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0008_school_types_subtypes'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='lesson_app',
            field=models.CharField(
                choices=[
                    ('sikshavahini', 'Sikshavahini'),
                    ('sunaadam', 'Sunaadam'),
                ],
                default='sikshavahini',
                help_text='Lesson application opened for users of this school.',
                max_length=20,
            ),
        ),
        migrations.RunPython(assign_music_schools, restore_sikshavahini),
    ]
