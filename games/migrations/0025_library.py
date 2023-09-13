# Generated by Django 4.1.5 on 2023-08-28 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0024_alter_backlogged_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.IntegerField()),
                ('game_name', models.CharField(max_length=200)),
                ('date_backlogged', models.DateField()),
                ('date_started', models.DateField()),
                ('date_completed', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='library', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'game_id')},
            },
        ),
    ]
