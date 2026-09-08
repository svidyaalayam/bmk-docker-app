from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='legacy_uid',
            field=models.CharField(
                blank=True,
                help_text='Firebase UID retained when an account is imported from the legacy system.',
                max_length=128,
                null=True,
                unique=True,
            ),
        ),
    ]
