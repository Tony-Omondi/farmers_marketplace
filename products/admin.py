from django.contrib import admin
from .models import Category, Product, ProductImage, RecipeCategory, Recipe

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "description")
    inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

@admin.register(RecipeCategory)
class RecipeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'prep_time', 'cook_time', 'created_at']
    list_filter = ['category', 'created_at']  # ✅ REMOVED 'tags'
    search_fields = ['title', 'description', 'ingredients']
    # ✅ REMOVED filter_horizontal = ['tags'] - taggit doesn't support it!
    readonly_fields = ['created_at', 'updated_at']