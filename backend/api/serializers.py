import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer as DjUserCreateSerializer
from django.shortcuts import get_object_or_404
from food.models import Ingredient, IngredientThrough, Recipe, Tag, User
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from users.models import Cart, Favorites, Subscription


class UserFilterMixin():
    """Mixin used for its method."""
    def user_is_on_it(self, user, model, somedict):
        """For the DRY."""
        if user.is_authenticated and model.objects.filter(**somedict).exists():

            return True

        return False


class RecipeSerializerCommon(serializers.ModelSerializer, UserFilterMixin):
    """Common base for inheritance. DRY."""
    class Meta:
        model = Recipe

    def get_is_favorited(self, object):
        """If recipes is favorited - returns True."""
        user = self.context['request'].user

        return self.user_is_on_it(
            user,
            Favorites,
            {'recipe': object.pk, 'user': user}
        )

    def get_is_in_shopping_cart(self, object):
        """If recipe is in shopping cart - returns True."""
        user = self.context['request'].user

        return self.user_is_on_it(
            user,
            Cart,
            {'recipe': object.pk, 'user': user}
        )


class DecodeImageField(serializers.ImageField):
    """Image field in Base64 encoding."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientShowSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for IngredientThrough model."""
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientThrough
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        """
        Returns Ingredient model instance.
        Some base validation implemented, rest skipped.
        """
        someid, amount = data.get('id'), data.get('amount')
        if IngredientThrough.objects.filter(id=someid, amount=amount).exists():
            someid = IngredientThrough.objects.select_related(
                'ingredient'
            ).get(id=someid, amount=amount).ingredient.id
        # Toss aside checking and just call get_object_or_404
        # should be possible?
        if not Ingredient.objects.filter(id=someid).exists():
            raise NotFound('No such ingredient')
        if not amount:
            raise serializers.ValidationError(
                'You must specify amount with int value'
            )

        return {
            'ingredient': Ingredient.objects.get(id=someid),
            'amount': amount
        }


class TagsSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        """Returns Tag model instance."""
        if not Tag.objects.filter(id=data).exists():
            raise NotFound('No such tag')

        return Tag.objects.get(id=data)


class UserSerializer(serializers.ModelSerializer, UserFilterMixin):
    """Serializer for User model."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, object):
        """If user is subscribed on object - returns True."""
        user = self.context['request'].user

        return self.user_is_on_it(
            user,
            Subscription,
            {'followed': object.pk, 'follower': user}
        )


class UserCreateSerializer(DjUserCreateSerializer):
    """Serializer for creating User model instances."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }


class RecipeInclusionSerializer(RecipeSerializerCommon):
    """Serializer for shortened representation of Recipe model."""
    class Meta(RecipeSerializerCommon.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')

    def to_internal_value(self, data):
        user = self.context['request'].user
        model = data.get('model')
        recipe = get_object_or_404(Recipe, pk=data.get('pk'))
        if model.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError({
                'non_fields_error':
                f'{model._meta.verbose_name} object already exists'
            })

        model.objects.create(recipe=recipe, user=user)

        return recipe


class RecipeSerializer(RecipeSerializerCommon):
    """Serializer for Recipe model."""
    ingredients = IngredientSerializer(many=True)
    tags = TagsSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = DecodeImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta(RecipeSerializerCommon.Meta):
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create_ingredients(self, ingredients, recipe):
        for dict_of_ingredients in ingredients:
            IngredientThrough.objects.create(
                recipe=recipe,
                **dict_of_ingredients
            )

    @transaction.atomic
    def create(self, validated_data):
        """Most logic here is for populating MToM related tables."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for key, value in (('ingredients', ingredients), ('tags', tags)):
            if not value:
                raise serializers.ValidationError(f'Empty value: {key}')

        image = validated_data.pop('image')
        if Recipe.objects.filter(**validated_data).exists():
            raise serializers.ValidationError(
                'You already created this recipe'
            )

        recipe = Recipe.objects.create(**validated_data, image=image)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def _duplicate_validation(self, attrs):
        """
        Check for duplicates in Tags and Ingredients.
        You can only add distinct objects of those models in Recipe instance.
        """
        final = []
        for attr in attrs:
            if attr in final:
                raise serializers.ValidationError(f'Duplicates: {attr}')
            final.append(attr)

    def validate(self, attrs):
        """
        Overriden validate method calls _duplicate_validation for some objects.
        """
        for doubt_value in (attrs.get('tags'), attrs.get('ingredients')):
            self._duplicate_validation(doubt_value)

        return super().validate(attrs)

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Most logic here is for re-populating MToM related tables.
        For Recipe model.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        if ingredients:
            instance.ingredients.all().delete()
            self.create_ingredients(ingredients, instance)

        return super().update(instance, validated_data)


class UserSubscriptionsSerializer(UserSerializer):
    """Serializer for subscriptions of User model."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, value):
        """Calls another serializer to display recipes with filtering."""
        recipes_limit = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        queryset = value.recipes.order_by('-date_created')
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            serializer = RecipeInclusionSerializer(
                queryset[:recipes_limit],
                many=True
            )
        else:
            serializer = RecipeInclusionSerializer(queryset, many=True)

        return serializer.data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for Subscription modedl."""
    class Meta:
        model = Subscription
        fields = ('follower', 'followed')

    def validate(self, attrs):
        """You can't follow yourself or already followed user."""
        user = attrs.get('follower')
        followed = attrs.get('followed')
        if user == followed:
            raise serializers.ValidationError('You can not follow yourself.')
        if Subscription.objects.filter(
            follower=user,
            followed=followed
        ).exists():
            raise serializers.ValidationError('You already follow this guy.')

        return attrs
