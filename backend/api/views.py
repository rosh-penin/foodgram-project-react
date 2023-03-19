from django.db.models import Q, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjUserViewSet
from food.models import Ingredient, IngredientThrough, Recipe, Tag
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.models import Cart, Favorites, Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientShowSerializer, RecipeInclusionSerializer,
                          RecipeSerializer, SubscriptionsSerializer,
                          TagsSerializer, UserSubscriptionsSerializer)


class IngredientViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Viewset for Ingredient model."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientShowSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    allowed_methods = ['GET']
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Viewset for Recipe model."""
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Returns queryset with filtering by tags and date."""
        condition = Q()
        tags = self.request.query_params.getlist('tags')
        for tag in tags:
            condition |= Q(tags__slug=tag)

        return Recipe.objects.filter(
            condition
        ).order_by('-date_created').distinct()

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        """Adding and removing recipe from shopping cart."""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Cart.objects.filter(recipe=recipe, user=request.user).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)

            Cart.objects.create(recipe=recipe, user=request.user)
            serializer = RecipeInclusionSerializer(recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Cart.objects.filter(
                recipe=recipe,
                user=request.user
            ).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)

            Cart.objects.filter(recipe=recipe, user=request.user).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request):
        """Returns .txt file with all ingredients combined."""
        file = 'Your Shopping List'
        ingredients = list(IngredientThrough.objects.filter(
            recipe__carts__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount')))
        for ingredient in ingredients:
            file += '\n{0} ({1}) - {2}'.format(*ingredient)

        response = FileResponse(file, as_attachment=True, filename='file.txt')
        response.set_headers(file)

        return response

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        """Add and remove recipe from favorites."""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Favorites.objects.filter(
                recipe=recipe,
                follower=request.user
            ).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)

            Favorites.objects.create(recipe=recipe, follower=request.user)
            serializer = RecipeInclusionSerializer(recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Favorites.objects.filter(
                recipe=recipe,
                follower=request.user
            ).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)

            Favorites.objects.filter(
                recipe=recipe,
                follower=request.user
            ).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        """Add user as author to recipe."""
        serializer.save(author=self.request.user)


class TagsViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Viewset for Tag model."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny]
    allowed_methods = ['GET']
    pagination_class = None


class UsersViewSet(DjUserViewSet):
    """Overriden djoset.views.UserViewSet."""
    queryset = User.objects.all()

    def get_permissions(self):
        """New permissions for new actions."""
        if self.action in ['subscriptions', 'subscribe']:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def get_serializer_class(self):
        """New serializers for new actions."""
        if self.action == 'subscriptions':

            return UserSubscriptionsSerializer

        if self.action == 'subscribe':

            return SubscriptionsSerializer

        return super().get_serializer_class()

    @action(['get'], detail=False)
    def subscriptions(self, request):
        """Returns all users that request.user follows."""
        user = request.user
        queryset = user.follows.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        """Subscribe and unsubscribe to user."""
        user = request.user
        if request.method == 'POST':
            serializer = self.get_serializer(
                data={'follower': user.id, 'followed': id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = UserSubscriptionsSerializer(
                User.objects.get(id=id),
                context={'request': request}
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            followed = get_object_or_404(User, id=id)
            instance = get_object_or_404(
                Subscription,
                follower=user,
                followed=followed
            )
            # Should be possible to just go by followed__id
            # without hitting db twice
            self.perform_destroy(instance)

            return Response(status=status.HTTP_204_NO_CONTENT)
