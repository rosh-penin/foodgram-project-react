from django.core.validators import RegexValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Component name', max_length=100)
    measurement_unit = models.CharField('Measurement unit', max_length=10)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('name', 'measurement_unit'), name='Ingredient_unique')]

    def __str__(self) -> str:
        return self.name


class IngredientThrough(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        models.CASCADE, # possible SET_NULL or DO_NOTHING?
        related_name='through'
    )
    recipe = models.ForeignKey(
        'Recipe',
        models.CASCADE,
        related_name='ingredients'
    )
    amount = models.IntegerField('Amount needed to use')


class Tag(models.Model):
    name = models.CharField('Tag name', max_length=20)
    color = models.CharField(
        'Hex color',
        max_length=7,
        validators=[RegexValidator(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")]
    )
    slug = models.SlugField('Tag slug', unique=True)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('recipe name', max_length=100)
    image = models.ImageField()
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.IntegerField('Time to finish cooking in minutes')
