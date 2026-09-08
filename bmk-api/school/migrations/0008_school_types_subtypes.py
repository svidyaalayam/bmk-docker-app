import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0007_homework_azure_storage'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='SchoolSubtype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=50)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                (
                    'school_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subtypes',
                        to='school.schooltype',
                    ),
                ),
            ],
            options={
                'ordering': ['display_order', 'name'],
                'unique_together': {('school_type', 'slug')},
            },
        ),
        migrations.AlterField(
            model_name='school',
            name='slug',
            field=models.CharField(
                help_text='Host prefix under the app domain, e.g. uk.telugu or balamukundam',
                max_length=100,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='school',
            name='domain',
            field=models.CharField(
                blank=True,
                help_text='Optional full hostname override, e.g. uk.telugu.balamukundam.com',
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='school',
            name='subtype',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='schools',
                to='school.schoolsubtype',
            ),
        ),
    ]
