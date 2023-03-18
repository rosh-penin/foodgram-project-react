from django.db.models import Q
from django_filters import rest_framework as filters


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(method='get_is_in_cart')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    author = filters.NumberFilter('author')

    def common_method_filter(self, queryset, dict_values, value):
        if value:
            return queryset.filter(**dict_values)

        return queryset.filter(~Q(**dict_values))

    def get_is_in_cart(self, queryset, name, value):

        return self.common_method_filter(queryset, {'carts__user': self.request.user}, value)
    
    def get_is_favorited(self, queryset, name, value):

        return self.common_method_filter(queryset, {'favorited__follower': self.request.user}, value)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter('name', 'icontains')
