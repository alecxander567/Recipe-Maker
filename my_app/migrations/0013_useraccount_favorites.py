# Generated by Django 5.1.7 on 2025-04-05 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0012_favoriterecipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='favorited_by', to='my_app.recipe'),
        ),
    ]
