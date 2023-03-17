import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from food.models import Recipe, Ingredient, Tag, User, IngredientThrough
from users.models import Subscription, Favorites, Cart


def user_is_on_it(user, model, somedict):
    if user.is_authenticated and model.objects.filter(**somedict):

        return True

    return False


class DecodeImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientShowSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientThrough
        fields = ('id', 'name', 'measurement_unit', 'amount')
    
    def to_internal_value(self, data):
        someid, amount = data.get('id'), data.get('amount')
        if IngredientThrough.objects.filter(id=someid, amount=amount).exists():
            someid = IngredientThrough.objects.select_related('ingredient').get(id=someid, amount=amount).ingredient.id
        if not Ingredient.objects.filter(id=someid).exists():
            raise NotFound('No such ingredient')
        if not amount:
            raise serializers.ValidationError('You must specify amount with int value')

        return {'ingredient': Ingredient.objects.get(id=someid), 'amount': amount}


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
    
    def to_internal_value(self, data):
        if not Tag.objects.filter(id=data).exists():
            raise NotFound('No such tag')

        return Tag.objects.get(id=data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, object):
        user = self.context['request'].user

        return user_is_on_it(user, Subscription, {'followed': object.pk, 'follower': user})


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True}}


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagsSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = DecodeImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for key, value in (('ingredients', ingredients), ('tags', tags)):
            if not value:
                raise serializers.ValidationError(f'Empty value: {key}')

        image = validated_data.pop('image')
        if Recipe.objects.filter(**validated_data).exists():
            raise serializers.ValidationError('You already created this recipe')

        recipe = Recipe.objects.create(**validated_data, image=image)
        recipe.tags.set(tags)
        for dict_of_ingredients in ingredients:
            IngredientThrough.objects.create(recipe=recipe, **dict_of_ingredients)

        return recipe
    
    def get_is_favorited(self, object):
        user = self.context['request'].user

        return user_is_on_it(user, Favorites, {'recipe': object.pk, 'follower': user})
    
    def get_is_in_shopping_cart(self, object):
        user = self.context['request'].user

        return user_is_on_it(user, Cart, {'recipe': object.pk, 'user': user})
    
    def dublicate_validation(self, attrs):
        final = []
        for attr in attrs:
            if attr in final:
                raise serializers.ValidationError(f'Duplicates: {attr}')
            final.append(attr)

    def validate(self, attrs):
        for doubt_value in (attrs.get('tags'), attrs.get('ingredients')):
            self.dublicate_validation(doubt_value)

        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        if ingredients:
            instance.ingredients.all().delete()
            for dict_of_ingredients in ingredients:
                IngredientThrough.objects.create(recipe=instance, **dict_of_ingredients)

        return super().update(instance, validated_data)


class RecipeInclusionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscriptionsSerializer(UserSerializer):
    recipes = RecipeInclusionSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')


class SubscriptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('follower', 'followed')
    
    def validate(self, attrs):
        user = attrs.get('follower')
        followed = attrs.get('followed')
        if user == followed:
            raise serializers.ValidationError('You can not follow yourself.')
        if Subscription.objects.filter(follower=user, followed=followed):
            raise serializers.ValidationError('You already follow this guy.')

        return attrs
