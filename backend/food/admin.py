from django.contrib import admin

from .models import Recipe, Ingredient, Tag, IngredientThrough

admin.site.register([Recipe, Ingredient, Tag, IngredientThrough])
