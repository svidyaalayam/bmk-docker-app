from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0022_student_account_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolsettings',
            name='unauthorised_absence_block_threshold',
            field=models.PositiveIntegerField(
                default=3,
                help_text='Consecutive unauthorised absences required before a teacher can block a student.',
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]
