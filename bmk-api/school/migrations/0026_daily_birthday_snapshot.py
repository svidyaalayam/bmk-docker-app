from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0025_terms_and_conditions'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyBirthdaySnapshot',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('snapshot_date', models.DateField(unique=True)),
                ('birthday_students', models.JSONField(default=list)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-snapshot_date'],
            },
        ),
    ]
