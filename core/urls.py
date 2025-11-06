# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    WarehouseViewSet,
    OrderViewSet,
    DashboardStatsView,
    RouteListView,
    CustomTokenObtainPairView,
    HealthCheckView,
    WarehouseListCreateView,
    WarehouseDetailView,
    ProductListCreateView,
)

# --- Router para ViewSets ---
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'orders', OrderViewSet, basename='order')

# --- URL patterns ---
urlpatterns = [
    path('', include(router.urls)),  # inclui rotas automáticas do router
    
    # Rotas adicionais (não baseadas em ViewSet)
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('routes/', RouteListView.as_view(), name='route-list'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # Rotas diretas (exemplo de endpoints específicos)
    path('warehouses/', WarehouseListCreateView.as_view(), name='warehouse-list'),
    path('warehouses/<str:uid>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
    path('products/', ProductListCreateView.as_view(), name='product-list'),
]
