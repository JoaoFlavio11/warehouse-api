# warehouse/urls.py
from django.urls import path
from .views import WarehouseListCreateView, WarehouseDetailView

urlpatterns = [
    path('', WarehouseListCreateView.as_view(), name='warehouse-list'),  # ✅ sem 'warehouses/'
    path('<str:uid>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
]