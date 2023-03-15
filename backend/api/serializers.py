import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers
from food.models import Recipe, Ingredient, Tag, User, IngredientThrough
from users.models import Subscription


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
        if not Ingredient.objects.filter(id=data.get('id')).exists():
            raise serializers.ValidationError('No such ingredient')

        return data


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
    
    def to_internal_value(self, data):
        if not Tag.objects.filter(id=data).exists():
            raise serializers.ValidationError('No such tag')

        return {'id': data}


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, object):
        user = self.context['request'].user
        if user.is_authenticated and user.subscriptions.filter(followed=object.pk):

            return True

        return False


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
    
    class Meta:
        model = Recipe
        # fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')

    def extract_ingredients_tags(self, data, model):
        somelist = []
        for object in data:
            if model.objects.filter(pk=object.get('id')).exists():
                amount = object.get('amount')
                if amount:
                    somelist.append((model.objects.get(pk=object.get('id')), amount))
                else:
                    somelist.append((model.objects.get(pk=object.get('id'))))

        return somelist

    def create(self, validated_data):
        ingredients = self.extract_ingredients_tags(validated_data.pop('ingredients'), Ingredient)
        tags = self.extract_ingredients_tags(validated_data.pop('tags'), Tag)

        recipe = Recipe.objects.create(**validated_data)
        if tags:
            recipe.tags.set(tags)

        for ingredient, amount in ingredients:
            IngredientThrough.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)

        return recipe
    
    def update(self, instance, validated_data):
        ingredients = self.extract_ingredients_tags(validated_data.pop('ingredients'), Ingredient)
        tags = self.extract_ingredients_tags(validated_data.pop('tags'), Tag)

        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        if ingredients:
            instance.ingredients.all().delete()
            for ingredient, amount in ingredients:
                IngredientThrough.objects.create(recipe=instance, ingredient=ingredient, amount=amount)

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
