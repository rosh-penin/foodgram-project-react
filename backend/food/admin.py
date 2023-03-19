from django.contrib import admin

from .models import Ingredient, IngredientThrough, Recipe, Tag


class IngredientsInLine(admin.TabularInline):
    model = IngredientThrough
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInLine,)


admin.site.register([Ingredient, Tag])
