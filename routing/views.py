from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsFirebaseAuthenticated
from .graph_algorithms import WarehouseGraph

class OptimalPickingRouteView(APIView):
  """ Rota ótima do picking para um pedido """
  permission_classes = [IsFirebaseAuthenticated]
  
  def post(self, request):
    """
      Body esperado:
      {
        "warehouse_uid": "uuid-do-warehouse",
        "bin_codes": ["A-01-02-A", "B-03-01-B", "A-02-04-C"]
      }
    """
    warehouse_uid = request.data.get('warehouse_uid')
    bin_codes = request.data.get('bin_codes', [])
    
    if not warehouse_uid or not bin_codes:
      return Response(
        {'error': 'warehouse_uid e bin_codes são obrigatórios'},
        status=status.HTTP_400_BAD_REQUEST
      )
    try:
      graph = WarehouseGraph(warehouse_uid)
      route = graph.find_optimal_picking_route(bin_codes)
            
      return Response({
        'success': True,
        'route': route,
        'optimization': 'TSP approximation algorithm'
      })
        
    except Exception as e:
      return Response(
        {'error': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

class ShortestPathView(APIView):
  """ Encontra o caminho mais curto entre dois bins """
  permission_classes = [IsFirebaseAuthenticated]
    
  def post(self, request):
  """
    Body esperado:
    {
      "warehouse_uid": "uuid",
      "start_bin": "A-01-02-A",
      "end_bin": "B-03-01-B"
    }
  """
  warehouse_uid = request.data.get('warehouse_uid')
  start_bin = request.data.get('start_bin')
  end_bin = request.data.get('end_bin')
        
  if not all([warehouse_uid, start_bin, end_bin]):
    return Response(
      {'error': 'Todos os campos são obrigatórios'},
      status=status.HTTP_400_BAD_REQUEST
    )
        
  try:
    graph = WarehouseGraph(warehouse_uid)
    path = graph.find_shortest_path(start_bin, end_bin)
            
    return Response({
      'success': True,
      'path': path
    })
        
    except Exception as e:
      return Response(
        {'error': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )