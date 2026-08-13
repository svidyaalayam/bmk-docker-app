import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('school', '0004_attendance_homework_submitted'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassSessionMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('kind', models.CharField(choices=[('CLASSWORK', 'Classwork'), ('HOMEWORK', 'Homework')], max_length=16)),
                ('file', models.FileField(upload_to='session_materials/%Y/%m/')),
                ('original_filename', models.CharField(blank=True, max_length=255)),
                ('content_type', models.CharField(blank=True, max_length=100)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='school.classsession')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['kind', 'created_at', 'id'],
            },
        ),
    ]
