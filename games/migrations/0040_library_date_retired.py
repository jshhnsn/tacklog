# Generated by Django 4.1.5 on 2025-03-30 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0039_library_platform_other_library_platform_playdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='library',
            name='date_retired',
            field=models.DateField(blank=True, null=True),
        ),
    ]
