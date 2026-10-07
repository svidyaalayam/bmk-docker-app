from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0034_announcement'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsession',
            name='homework_due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
