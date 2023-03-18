from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjUserViewSet
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from food.models import Recipe, Tag, Ingredient
from users.models import User, Subscription, Favorites, Cart

from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import RecipeSerializer, RecipeInclusionSerializer, TagsSerializer, IngredientShowSerializer, UserSubscriptionsSerializer, SubscriptionsSerializer


class IngredientViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientShowSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    allowed_methods = ['GET']
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    # queryset = Recipe.objects.order_by('date_created')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter

    def get_queryset(self):
        condition = Q()
        tags = self.request.query_params.getlist('tags')
        for tag in tags:
            condition |= Q(tags__slug=tag)

        return Recipe.objects.filter(condition).order_by('-date_created')
    
    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Cart.objects.filter(recipe=recipe, user=request.user).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            Cart.objects.create(recipe=recipe, user=request.user)
            serializer = RecipeInclusionSerializer(recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Cart.objects.filter(recipe=recipe, user=request.user).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)

            Cart.objects.filter(recipe=recipe, user=request.user).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(['get'], detail=False)
    def download_shopping_cart(self, request):
        file = 'Your Shopping List'
        somedict = dict()
        for cart in request.user.carts.all():
            for ingredient in cart.recipe.ingredients.all():
                key = f'{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})'
                if somedict.get(key):
                    somedict[key] += ingredient.amount
                else:
                    somedict[key] = ingredient.amount

        for k, v in somedict.items():
            file = file + f'\n{k} - {v}'
        
        response = HttpResponse(file, content_type='text/plain; charset=utf8')
        response['Content-Disposition'] = 'attachment; filename=ShoppingCart.txt'

        return response

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Favorites.objects.filter(recipe=recipe, follower=request.user).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            Favorites.objects.create(recipe=recipe, follower=request.user)
            serializer = RecipeInclusionSerializer(recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            if not Favorites.objects.filter(recipe=recipe, follower=request.user).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)

            Favorites.objects.filter(recipe=recipe, follower=request.user).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagsViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny]
    allowed_methods = ['GET']
    pagination_class = None


class UsersViewSet(DjUserViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action in ['subscriptions', 'subscribe']:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'subscriptions':

            return UserSubscriptionsSerializer

        if self.action == 'subscribe':

            return SubscriptionsSerializer

        return super().get_serializer_class()
    
    @action(['get'], detail=False)
    def subscriptions(self, request):
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
        user = request.user
        if request.method == 'POST':
            serializer = self.get_serializer(data={'follower': user.id, 'followed': id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = UserSubscriptionsSerializer(User.objects.get(id=id), context={'request': request})

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            followed = get_object_or_404(User, id=id)
            instance = get_object_or_404(Subscription, follower=user, followed=followed)
            # Should be possible to just go by followed__id without hitting db twice. Or not.
            self.perform_destroy(instance)

            return Response(status=status.HTTP_204_NO_CONTENT)
