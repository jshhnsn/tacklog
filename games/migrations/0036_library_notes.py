# Generated by Django 4.1.5 on 2023-08-30 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0035_library_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='library',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
