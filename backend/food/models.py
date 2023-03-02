from django.db import models
from users.models import User


class Unit(models.Model):
    unit = models.CharField('Measurement unit', max_length=10)


class ComponentName(models.Model):
    name = models.CharField('Component name', max_length=100)


class Component(models.Model):
    name = models.ForeignKey(
        ComponentName,
        models.CASCADE,
        related_name='components'
    )
    unit = models.ForeignKey(
        Unit,
        models.CASCADE,
        related_name='components'
    )
    amount = models.IntegerField('Amount of component')


class Tag(models.Model):
    name = models.CharField('Tag name', max_length=20)
    hex = models.CharField('Hex color', max_length=6)
    slug = models.SlugField('Tag slug')


class Receipt(models.Model):
    author = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='receipts'
    )
    name = models.CharField('Receipt name', max_length=100)
    image = models.ImageField()
    description = models.TextField()
    components = models.ManyToManyField(
        Component,
        related_name='receipts'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='receipts'
    )