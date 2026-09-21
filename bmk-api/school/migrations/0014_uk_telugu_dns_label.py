from django.db import migrations, models


def rename_uk_telugu_to_dns_label(apps, schema_editor):
    """Move the legacy dotted UK Telugu tenant to its single-label hostname."""
    School = apps.get_model('school', 'School')
    dotted = School.objects.filter(slug='uk.telugu').first()
    if not dotted:
        return

    canonical = School.objects.filter(slug='uk-telugu').first()
    if canonical:
        # A partly completed deployment may already have created the canonical
        # tenant. Preserve it and move all related data before removing the old row.
        for relation in School._meta.related_objects:
            if not relation.one_to_many and not relation.one_to_one:
                continue
            related_model = relation.related_model
            field_name = relation.field.name
            related = related_model.objects.filter(**{field_name: dotted})
            if relation.one_to_one and related_model.objects.filter(
                **{field_name: canonical}
            ).exists():
                related.delete()
            else:
                related.update(**{field_name: canonical})
        dotted.delete()
        return

    dotted.slug = 'uk-telugu'
    if dotted.domain == 'uk.telugu.localhost':
        dotted.domain = 'uk-telugu.localhost'
    dotted.save(update_fields=['slug', 'domain'])


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0013_school_school_number'),
    ]

    operations = [
        migrations.RunPython(rename_uk_telugu_to_dns_label, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='school',
            name='slug',
            field=models.CharField(
                help_text='Host prefix under the app domain, e.g. uk-telugu or balamukundam',
                max_length=100,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='school',
            name='domain',
            field=models.CharField(
                blank=True,
                help_text='Optional full hostname override, e.g. uk-telugu.balamukundam.com',
                max_length=255,
            ),
        ),
    ]
