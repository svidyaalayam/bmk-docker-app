from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0006_alter_user_legacy_uid'),
        ('school', '0016_remove_school_programmes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='school',
        ),
    ]
