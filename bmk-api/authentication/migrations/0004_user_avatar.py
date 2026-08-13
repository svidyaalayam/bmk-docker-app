from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_user_email_verified_profile_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(
                blank=True,
                help_text='Optional profile photo shown as the user avatar.',
                null=True,
                upload_to='avatars/%Y/%m/',
            ),
        ),
    ]
