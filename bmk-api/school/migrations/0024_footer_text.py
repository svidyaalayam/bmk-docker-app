from django.db import migrations, models


FOOTER_TEXT = (
    'బాలముకుందము ఔత్సాహికులయిన ఉపాధ్యాయులు, స్వచ్చందంగా అందిస్తున్న సేవల ఆధారంగా '
    'నిర్వహింపబడుతున్న ధార్మిక విద్యాసంస్థ. మా పాఠశాలలో పాఠములు, పరీక్షలు, పుస్తకములు '
    'వంటి బోధనాంశములు అన్ని విద్యార్థులకు ఉచితముగా అందజేయబడును. email:bmtsuk@gmail.com'
)


def set_default_footer(apps, schema_editor):
    SchoolSettings = apps.get_model('school', 'SchoolSettings')
    SchoolSettings.objects.filter(pk=1).update(footer_text=FOOTER_TEXT)


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0023_absence_block_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolsettings',
            name='footer_text',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.RunPython(set_default_footer, migrations.RunPython.noop),
    ]
