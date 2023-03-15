from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagsViewSet, IngredientViewSet, UsersViewSet

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
