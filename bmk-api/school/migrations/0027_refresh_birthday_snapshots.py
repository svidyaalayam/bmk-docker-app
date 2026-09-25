from django.db import migrations


def refresh_snapshots(apps, schema_editor):
    DailyBirthdaySnapshot = apps.get_model('school', 'DailyBirthdaySnapshot')
    DailyBirthdaySnapshot.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0026_daily_birthday_snapshot'),
    ]

    operations = [
        migrations.RunPython(refresh_snapshots, migrations.RunPython.noop),
    ]
