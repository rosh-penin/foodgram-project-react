from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Overriden User model."""
    email = models.EmailField("Email address", unique=True)
    password = models.CharField("password", max_length=150)
    first_name = models.CharField('First Name', max_length=150)
    last_name = models.CharField('Last Name', max_length=150)
    follows = models.ManyToManyField(
        'self',
        through='Subscription',
        symmetrical=False
    )
    favorites_recipes = models.ManyToManyField(
        'food.Recipe',
        'Favorites'
    )


class Subscription(models.Model):
    """Through model for MToM relation User-User model."""
    follower = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='subscriptions'
    )
    followed = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='followers'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=('follower', 'followed'),
            name='only_one_sub_for_pair_of_users'
        )]


class Favorites(models.Model):
    """
    Through model for MToM relation User-Recipe models.
    Favorites.
    """
    follower = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        'food.Recipe',
        models.CASCADE,
        related_name='favorited'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=('follower', 'recipe'),
            name='Favorites_unique'
        )]


class Cart(models.Model):
    """
    Through model for MToM relation User-Recipe models.
    Shopping cart.
    """
    recipe = models.ForeignKey(
        'food.Recipe',
        models.CASCADE,
        related_name='carts'
    )
    user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='carts'
    )
