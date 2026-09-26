from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0027_refresh_birthday_snapshots'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicCalendarEntry',
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entry_type', models.CharField(
                    choices=[('TERM', 'Term'), ('HOLIDAY', 'Holiday')],
                    max_length=12,
                )),
                ('title', models.CharField(max_length=200)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=models.SET_NULL,
                    related_name='academiccalendarentry_created',
                    to='authentication.user',
                )),
                ('updated_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=models.SET_NULL,
                    related_name='academiccalendarentry_updated',
                    to='authentication.user',
                )),
            ],
            options={
                'ordering': ['start_date', 'display_order', 'title'],
            },
        ),
    ]
