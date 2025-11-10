#routing/urls.py
from django.urls import path
from .views import OptimalPickingRouteView, ShortestPathView, RoutingHealthView

urlpatterns = [
    path('', RoutingHealthView.as_view(), name='routing-health'),
    path('picking-route/', OptimalPickingRouteView.as_view(), name='picking-route'),
    path('shortest-path/', ShortestPathView.as_view(), name='shortest-path'),
]
