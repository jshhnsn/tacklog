# Generated by Django 4.1.5 on 2023-01-30 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0002_alter_backlogged_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backlogged',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='backlog', to=settings.AUTH_USER_MODEL),
        ),
    ]
