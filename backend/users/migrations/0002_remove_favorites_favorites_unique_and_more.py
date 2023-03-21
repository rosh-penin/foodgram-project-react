# Generated by Django 4.1.7 on 2023-03-21 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorites',
            name='Favorites_unique',
        ),
        migrations.RenameField(
            model_name='favorites',
            old_name='follower',
            new_name='user',
        ),
        migrations.AddConstraint(
            model_name='cart',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='Carts_unique'),
        ),
        migrations.AddConstraint(
            model_name='favorites',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='Favorites_unique'),
        ),
    ]
