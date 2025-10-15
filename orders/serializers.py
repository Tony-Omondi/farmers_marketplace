from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, Coupon
from products.models import Product
from products.serializers import ProductSerializer  # Import existing ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'created_at', 'updated_at']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    coupon = serializers.PrimaryKeyRelatedField(queryset=Coupon.objects.filter(active=True), required=False, allow_null=True)

    class Meta:
        model = Cart
        fields = ['id', 'uid', 'user', 'is_paid', 'coupon', 'cart_items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'is_paid', 'cart_items', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    # ✅ FULL PRODUCT DETAILS + EXTRAS
    product = ProductSerializer(read_only=True)  # Complete product info
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'created_at', 'updated_at']

# ✅ NEW: For Order Creation (minimal fields)
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = []  # Empty - all handled in view

# ✅ NEW: For Order Status Updates (matches admin!)
class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']  # Only status editable!

class OrderSerializer(serializers.ModelSerializer):
    # ✅ FULL ORDER ITEMS + COUPON + STATUS EXPOSED
    order_items = OrderItemSerializer(many=True, read_only=True)
    coupon = serializers.SerializerMethodField()  # Better coupon display
    status = serializers.CharField(read_only=True)  # ✅ EXPOSED FOR FILTERING
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'user', 'payment_status', 'payment_mode', 
            'status', 'coupon', 'total_amount', 'order_items', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'order_id', 'payment_status', 'payment_mode', 
            'status', 'total_amount', 'order_items', 'created_at', 'updated_at'
        ]

    def get_coupon(self, obj):
        """Return coupon code or None"""
        return {'coupon_code': obj.coupon.coupon_code} if obj.coupon else None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'reference', 'payment_status', 'created_at', 'updated_at']
        read_only_fields = ['order', 'amount', 'reference', 'payment_status', 'created_at', 'updated_at']