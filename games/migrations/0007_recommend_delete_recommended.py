# Generated by Django 4.1.5 on 2023-02-12 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0006_recommended_delete_recommendations'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_recommended', models.DateField(auto_now=True)),
                ('backlog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommended', to='games.backlogged')),
            ],
        ),
        migrations.DeleteModel(
            name='Recommended',
        ),
    ]
