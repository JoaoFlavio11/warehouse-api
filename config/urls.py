from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('warehouse.urls')),
    path('api/routing/', include('routing.urls')),
]