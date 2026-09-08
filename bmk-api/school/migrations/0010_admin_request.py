from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('school', '0009_school_lesson_app')]
    operations = [
        migrations.CreateModel(
            name='AdminRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('REQUEST', 'Request'), ('FEEDBACK', 'Feedback / suggestion')], max_length=16)),
                ('subject', models.CharField(max_length=200)), ('message', models.TextField()), ('reply', models.TextField(blank=True)),
                ('resolved', models.BooleanField(default=False)), ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('replied_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_request_replies', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_requests', to='school.school')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_requests', to=settings.AUTH_USER_MODEL)),
            ], options={'ordering': ['-created_at', '-id']},
        )
    ]
