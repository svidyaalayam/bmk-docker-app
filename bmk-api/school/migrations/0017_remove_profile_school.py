from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0007_remove_user_school'),
        ('school', '0016_remove_school_programmes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='school',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='school',
        ),
    ]
