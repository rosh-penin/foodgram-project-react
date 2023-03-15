# Generated by Django 4.1.7 on 2023-03-13 13:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Component name')),
                ('measurement_unit', models.CharField(max_length=10, verbose_name='Measurement unit')),
            ],
        ),
        migrations.CreateModel(
            name='IngredientThrough',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='Amount needed to use')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='recipe name')),
                ('image', models.ImageField(upload_to='')),
                ('text', models.TextField()),
                ('cooking_time', models.IntegerField(verbose_name='Time to finish cooking in minutes')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Tag name')),
                ('color', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Hex color')),
                ('slug', models.SlugField(unique=True, verbose_name='Tag slug')),
            ],
        ),
    ]
