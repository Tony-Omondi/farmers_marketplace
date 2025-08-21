# adamin/views.py
from rest_framework import generics, serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order, OrderItem, Payment, Coupon
from orders.serializers import OrderSerializer, PaymentSerializer  # Fixed import
from products.models import Product, Category
from products.serializers import ProductSerializer, CategorySerializer
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category']
    search_fields = ['name', 'description']

class CategoryListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OrderListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_fields = ['status', 'payment_status']
    search_fields = ['order_id', 'user__email']

class PaymentListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer  # Correct reference
    search_fields = ['reference', 'order__order_id']

class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = serializers.Serializer
    def get(self, request):
        email = request.query_params.get('email', '')
        users = User.objects.filter(email__icontains=email, is_active=True)
        return Response([{'email': user.email, 'full_name': user.full_name} for user in users])

class OrderCreateView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        user_email = request.data.get('user_email')
        items = request.data.get('items', [])
        coupon_code = request.data.get('coupon_code')
        payment_mode = request.data.get('payment_mode', 'Cash')
        try:
            user = User.objects.get(email=user_email, is_active=True)
            total_amount = 0
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                total_amount += Decimal(product.price) * item['quantity']
            if coupon_code:
                coupon = Coupon.objects.get(coupon_code=coupon_code, active=True)
                total_amount -= Decimal(coupon.discount)
            order = Order.objects.create(
                user=user,
                order_id=str(uuid.uuid4()),
                payment_status="completed" if payment_mode == "Cash" else "pending",
                payment_mode=payment_mode,
                status="confirmed",
                coupon=coupon if coupon_code else None,
                total_amount=max(total_amount, 0)
            )
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    product_price=Decimal(product.price)
                )
                product.stock -= item['quantity']
                product.save()
            if payment_mode == "Cash":
                Payment.objects.create(
                    order=order,
                    amount=total_amount,
                    payment_status="completed",
                    reference=str(uuid.uuid4())
                )
            return Response({"status": True, "order_id": order.order_id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"status": False, "message": "User not found or not active"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"status": False, "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Coupon.DoesNotExist:
            return Response({"status": False, "message": "Invalid or inactive coupon"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)