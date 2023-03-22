from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Model for ingredients."""
    name = models.CharField('Component name', max_length=100)
    measurement_unit = models.CharField('Measurement unit', max_length=10)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [models.UniqueConstraint(
            fields=('name', 'measurement_unit'),
            name='Ingredient_unique'
        )]

    def __str__(self) -> str:
        return self.name


class IngredientThrough(models.Model):
    """
    A through model for MToM relation between Recipe and Ingredient models.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        models.CASCADE,
        related_name='through'
    )
    recipe = models.ForeignKey(
        'Recipe',
        models.CASCADE,
        related_name='ingredients'
    )
    amount = models.IntegerField('Amount needed to use')

    class Meta:
        verbose_name = 'IngredientInRecipe'
        verbose_name_plural = 'IngredientsInRecipe'

    def __str__(self) -> str:
        return f'{self.ingredient.name} in {self.recipe.name}'


class Tag(models.Model):
    """Model for tags."""
    name = models.CharField('Tag name', max_length=20)
    color = models.CharField(
        'Hex color',
        max_length=7,
        validators=[RegexValidator(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")]
    )
    slug = models.SlugField('Tag slug', unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Model for recipes."""
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
    cooking_time = models.IntegerField(
        'Time to finish cooking in minutes',
        validators=[MinValueValidator(1)]
    )
    date_created = models.DateTimeField(
        'Time and date of creation',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return self.name
