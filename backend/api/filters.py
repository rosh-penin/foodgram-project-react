from django.db.models import Q
from django_filters import rest_framework as filters


class RecipeFilter(filters.FilterSet):
    """Custom Filterset for Recipe Viewset."""
    is_in_shopping_cart = filters.BooleanFilter(method='get_is_in_cart')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    author = filters.NumberFilter('author')

    def common_method_filter(self, queryset, dict_values, value):
        """Just DRY."""
        if value:
            return queryset.filter(**dict_values)

        return queryset.filter(~Q(**dict_values))

    def get_is_in_cart(self, queryset, name, value):
        """Returns filtered queryset for recipes in cart."""
        return self.common_method_filter(
            queryset,
            {'carts__user': self.request.user},
            value
        )

    def get_is_favorited(self, queryset, name, value):
        """Returns filtered queryset for favorited recipes."""
        return self.common_method_filter(
            queryset,
            {'favorited__follower': self.request.user},
            value
        )


class IngredientFilter(filters.FilterSet):
    """Filterset that allows filtering by ingredient name."""
    name = filters.CharFilter('name', 'icontains')
