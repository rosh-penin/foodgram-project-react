from django.contrib import admin

from .models import Ingredient, IngredientThrough, Recipe, Tag


class IngredientsInLine(admin.TabularInline):
    """For correct representation in admin panel."""
    model = IngredientThrough
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe model for admin panel."""
    inlines = (IngredientsInLine,)


admin.site.register([Ingredient, Tag])
