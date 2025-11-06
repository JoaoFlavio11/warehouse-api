from django.urls import path
from .views import OptimalPickingRouteView, ShortestPathView
from .views import OptimalPickingRouteView, ShortestPathView, RouteListView

urlpatterns = [
  path('', RouteListView.as_view(), name='route-list'),
  path('picking-route/', OptimalPickingRouteView.as_view(), name='picking-route'),
  path('shortest-path/', ShortestPathView.as_view(), name='shortest-path'),
]