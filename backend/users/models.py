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
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [models.UniqueConstraint(
            fields=('follower', 'followed'),
            name='only_one_sub_for_pair_of_users'
        )]

    def __str__(self) -> str:
        return f'{self.follower.username} follows {self.followed.username}'


class Favorites(models.Model):
    """
    Through model for MToM relation User-Recipe models.
    Favorites.
    """
    user = models.ForeignKey(
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
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='Favorites_unique'
        )]

    def __str__(self) -> str:
        return f'{self.user.username} favorites {self.recipe.name}'


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

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        constraints = [models.UniqueConstraint(
            fields=('recipe', 'user'),
            name='Carts_unique'
        )]

    def __str__(self) -> str:
        return f'{self.recipe.name} in cart of {self.user.username}'
