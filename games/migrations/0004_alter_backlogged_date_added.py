# Generated by Django 4.1.5 on 2023-02-11 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_alter_backlogged_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backlogged',
            name='date_added',
            field=models.DateField(auto_now=True),
        ),
    ]
