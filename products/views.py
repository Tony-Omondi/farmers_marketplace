from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Category, Recipe, RecipeCategory
from .serializers import ProductSerializer, CategorySerializer, RecipeSerializer, RecipeCategorySerializer
from django.db.models import Q

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ✅ NEW RECIPE VIEWS (ADD THESE)
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('category', 'author').prefetch_related('tags')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        category = self.request.query_params.get('category', '')
        tag = self.request.query_params.get('tag', '')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(ingredients__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__slug=category)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)
        return queryset.distinct()

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        recipe = self.get_object()
        similar = Recipe.objects.filter(category=recipe.category).exclude(pk=pk)[:4]
        serializer = self.get_serializer(similar, many=True)
        return Response(serializer.data)

class RecipeCategoryViewSet(viewsets.ModelViewSet):
    queryset = RecipeCategory.objects.all()
    serializer_class = RecipeCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]