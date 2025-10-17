from rest_framework import serializers
from django.utils.text import slugify
from .models import Product, ProductImage, Category, Recipe, RecipeCategory

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if obj.image else None

    class Meta:
        model = ProductImage
        fields = ["id", "image"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "category", "images", "image_files", "created_at", "updated_at"]

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        product = Product.objects.create(**validated_data)
        for image_file in image_files:
            ProductImage.objects.create(product=product, image=image_file)
        return product

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

# ✅ FIXED! Your RecipeCategorySerializer with UNIQUE SLUG LOGIC
class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ["id", "name", "slug", "description"]
    
    def validate_name(self, value):
        # Prevent duplicate names (case-insensitive)
        if self.instance is None:  # Creating new
            if RecipeCategory.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError(
                    f'Category "{value}" already exists. Please use a different name.'
                )
        return value
    
    def create(self, validated_data):
        # Generate UNIQUE slug automatically
        name = validated_data['name']
        slug = slugify(name)
        
        # Make slug unique by appending counter if needed
        original_slug = slug
        counter = 1
        while RecipeCategory.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        validated_data['slug'] = slug
        return super().create(validated_data)

class RecipeSerializer(serializers.ModelSerializer):
    category = RecipeCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=RecipeCategory.objects.all(), 
        source='category', 
        write_only=True, 
        allow_null=True
    )
    author = serializers.StringRelatedField(read_only=True)
    tags = serializers.ListField(child=serializers.CharField(max_length=50), write_only=True, required=False)
    tags_display = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    def get_tags_display(self, obj):
        return list(obj.tags.names())

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'image', 'image_url', 'description', 'ingredients', 
            'instructions', 'review', 'prep_time', 'cook_time', 'servings',
            'category', 'category_id', 'tags', 'tags_display', 'author', 
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        
        if tags_data:
            from taggit.models import Tag
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None:
            instance.tags.clear()
            from taggit.models import Tag
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                instance.tags.add(tag)
        return super().update(instance, validated_data)

# ✅ FIXED: AdminRecipeSerializer WITH image_url!
class AdminRecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ['id', 'name', 'slug', 'description']

class AdminRecipeSerializer(serializers.ModelSerializer):
    category = AdminRecipeCategorySerializer()
    tags_list = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()  # ✅ FIXED!
    
    def get_tags_list(self, obj):
        return list(obj.tags.names())
    
    def get_image_url(self, obj):  # ✅ FIXED!
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None
    
    class Meta:
        model = Recipe
        fields = '__all__'