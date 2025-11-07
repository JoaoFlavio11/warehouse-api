# core/urls.py
from django.urls import path
from .views import (
    WarehouseListCreateView,
    WarehouseDetailView,
    ProductListCreateView,
    HealthCheckView,
    #DashboardStatsView
)

urlpatterns = [
  path('health/', HealthCheckView.as_view(), name='health-check'),  
  path('warehouses/', WarehouseListCreateView.as_view(), name='warehouse-list'),
  path('warehouses/<str:uid>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
  path('products/', ProductListCreateView.as_view(), name='product-list'),
]
