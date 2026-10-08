from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0035_classsession_homework_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolsettings',
            name='open_student_registration',
            field=models.BooleanField(
                default=False,
                help_text='Allow new students to register. Teacher registration is always available.',
            ),
        ),
    ]
