from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0005_classsessionmaterial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolsettings',
            name='logo',
            field=models.ImageField(
                blank=True,
                help_text='School logo shown in the site header and school pages.',
                null=True,
                upload_to='school_logos/%Y/%m/',
            ),
        ),
    ]
