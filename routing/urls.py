from django.urls import path
from .views import OptimalPickingRouteView, ShortestPathView

urlpatterns = [
  path('picking-route/', OptimalPickingRouteView.as_view(), name='picking-route'),
  path('shortest-path/', ShortestPathView.as_view(), name='shortest-path'),
]