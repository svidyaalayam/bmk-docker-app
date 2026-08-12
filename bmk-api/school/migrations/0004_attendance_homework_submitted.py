from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0003_teaching_classes'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsessionattendance',
            name='homework_submitted',
            field=models.BooleanField(
                default=False,
                help_text='Student-declared homework submission for this session.',
            ),
        ),
    ]
