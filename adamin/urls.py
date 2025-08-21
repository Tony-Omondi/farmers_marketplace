from django.urls import path
from .views import ProductListCreateView, CategoryListView, OrderListView, PaymentListView, UserSearchView, OrderCreateView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='admin-product-list-create'),
    path('categories/', CategoryListView.as_view(), name='admin-category-list'),
    path('orders/', OrderListView.as_view(), name='admin-order-list'),
    path('payments/', PaymentListView.as_view(), name='admin-payment-list'),
    path('users/', UserSearchView.as_view(), name='admin-user-search'),
    path('orders/create/', OrderCreateView.as_view(), name='admin-order-create'),
]