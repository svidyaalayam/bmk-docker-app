from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('school', '0010_admin_request')]
    operations = [migrations.CreateModel(name='StudentTeacherRequest', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('kind', models.CharField(choices=[('REQUEST', 'Request'), ('FEEDBACK', 'Feedback / suggestion')], max_length=16)),
        ('subject', models.CharField(max_length=200)), ('message', models.TextField()), ('reply', models.TextField(blank=True)),
        ('resolved', models.BooleanField(default=False)), ('resolved_at', models.DateTimeField(blank=True, null=True)),
        ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
        ('replied_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_teacher_request_replies', to=settings.AUTH_USER_MODEL)),
        ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_teacher_requests', to='school.school')),
        ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_requests', to='school.student')),
        ('teaching_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_teacher_requests', to='school.teachingclass')),
    ], options={'ordering': ['-created_at', '-id']})]
