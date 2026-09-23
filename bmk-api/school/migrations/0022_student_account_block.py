from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0021_remove_kannada_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='account_blocked',
            field=models.BooleanField(
                default=False,
                help_text='Blocked students cannot access classes until an admin unblocks them.',
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='block_reason',
            field=models.TextField(blank=True),
        ),
    ]
