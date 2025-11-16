from django.urls import path
from .views import OrderListCreateView, OrderDetailView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list'),
    path('<str:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
