# Generated by Django 4.1.5 on 2023-08-28 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0026_alter_library_date_backlogged_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='library',
            name='date_backlogged',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='library',
            name='date_completed',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='library',
            name='date_started',
            field=models.DateField(blank=True, null=True),
        ),
    ]
