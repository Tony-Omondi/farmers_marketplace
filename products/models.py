from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return f"Image for {self.product.name}"

# ✅ ADD THESE RECIPE MODELS (SEPARATE FROM PRODUCT!)
class RecipeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Recipe Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    description = models.TextField(help_text="Short description or story behind the recipe.")
    ingredients = models.TextField(help_text="List ingredients separated by commas or line breaks.")
    instructions = models.TextField(help_text="Step-by-step cooking instructions.")
    review = models.TextField(blank=True, null=True)
    prep_time = models.CharField(max_length=50, help_text="e.g. 10 minutes")
    cook_time = models.CharField(max_length=50, help_text="e.g. 15 minutes")
    servings = models.PositiveIntegerField(default=1)

    # ✅ SEPARATE RecipeCategory (not shared with Product!)
    category = models.ForeignKey(RecipeCategory, on_delete=models.SET_NULL, null=True, related_name="recipes")
    tags = TaggableManager(help_text="Add tags like 'Kenyan', 'Vegan', 'Spicy', etc.")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title