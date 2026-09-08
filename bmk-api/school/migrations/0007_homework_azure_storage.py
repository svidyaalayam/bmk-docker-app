import school.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_schoolsettings_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsessionmaterial',
            name='storage_backend',
            field=models.CharField(
                default='local',
                help_text='local or azure_blob',
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name='classsessionmaterial',
            name='storage_uri',
            field=models.CharField(
                blank=True,
                help_text='Blob URL or local media path reference.',
                max_length=1000,
            ),
        ),
        migrations.AlterField(
            model_name='classsessionhomework',
            name='file',
            field=models.FileField(
                blank=True,
                storage=school.storage.select_homework_storage,
                upload_to=school.storage.student_homework_upload_to,
            ),
        ),
        migrations.AlterField(
            model_name='classsessionhomework',
            name='storage_backend',
            field=models.CharField(
                default='local',
                help_text='local or azure_blob',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='classsessionhomework',
            name='storage_uri',
            field=models.CharField(
                blank=True,
                help_text='Blob URL (possibly with SAS) or local media path reference.',
                max_length=1000,
            ),
        ),
        migrations.AlterField(
            model_name='classsessionmaterial',
            name='file',
            field=models.FileField(
                blank=True,
                storage=school.storage.select_homework_storage,
                upload_to=school.storage.session_material_upload_to,
            ),
        ),
    ]
