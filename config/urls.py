# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rotas principais da API
    path('api/warehouses/', include('warehouse.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/products/', include('products.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/reports/', include('reports.urls')),

    # Rotas sem prefixo
    path('warehouses/', include('warehouse.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('analytics/', include('analytics.urls')),
    path('reports/', include('reports.urls')),
]
