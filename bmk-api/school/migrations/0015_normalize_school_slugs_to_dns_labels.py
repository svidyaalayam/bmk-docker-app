from django.db import migrations


def move_related_objects(School, source, destination):
    for relation in School._meta.related_objects:
        if not relation.one_to_many and not relation.one_to_one:
            continue
        related_model = relation.related_model
        field_name = relation.field.name
        related = related_model.objects.filter(**{field_name: source})
        if relation.one_to_one and related_model.objects.filter(
            **{field_name: destination}
        ).exists():
            related.delete()
        else:
            related.update(**{field_name: destination})


def normalize_school_slugs(apps, schema_editor):
    School = apps.get_model('school', 'School')
    for school in School.objects.filter(slug__contains='.').order_by('pk'):
        old_slug = school.slug
        dns_label = old_slug.replace('.', '-')
        existing = School.objects.filter(slug=dns_label).exclude(pk=school.pk).first()
        if existing:
            move_related_objects(School, school, existing)
            school.delete()
            continue

        school.slug = dns_label
        if school.domain.startswith(f'{old_slug}.'):
            school.domain = f'{dns_label}{school.domain[len(old_slug):]}'
        school.save(update_fields=['slug', 'domain'])


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0014_uk_telugu_dns_label'),
    ]

    operations = [
        migrations.RunPython(normalize_school_slugs, migrations.RunPython.noop),
    ]
