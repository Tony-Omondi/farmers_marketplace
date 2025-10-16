from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, 
    RecipeViewSet, RecipeCategoryViewSet  # ✅ ADDED
)

router = DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"recipes", RecipeViewSet)  # ✅ ADDED
router.register(r"recipe-categories", RecipeCategoryViewSet)  # ✅ ADDED

urlpatterns = [
    path("", include(router.urls)),
]