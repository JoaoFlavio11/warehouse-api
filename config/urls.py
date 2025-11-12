# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/warehouses/', include('warehouse.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/products/', include('products.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('warehouses/', include('warehouse.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('routing/', include('routing.urls')),
    path('analytics/', include('analytics.urls')),
    path('reports/', include('reports.urls')),
]
