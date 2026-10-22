from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('school', '0036_schoolsettings_open_student_registration')]
    operations = [
        migrations.AddField(model_name='announcement', name='email_recipient_count', field=models.PositiveIntegerField(default=0, editable=False)),
        migrations.AddField(model_name='announcement', name='email_sent_at', field=models.DateTimeField(blank=True, editable=False, null=True)),
        migrations.AddField(model_name='announcement', name='email_sent_by', field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_announcements', to=settings.AUTH_USER_MODEL)),
    ]
