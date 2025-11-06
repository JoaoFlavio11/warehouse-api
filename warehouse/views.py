from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsFirebaseAuthenticated
from core.firebase_auth import firebase_auth_required
from .models import Warehouse, Zone, Product, Bin
from .serializers import WarehouseSerializer, ZoneSerializer, ProductSerializer, BinSerializer

class WarehouseListCreateView(APIView):
  # permission_classes = [IsFirebaseAuthenticated] # Removido para usar o decorador
  @firebase_auth_required
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)
  
  def get(self, request):
    """ listar os galpões/warehouses"""
    warehouses = Warehouse.nodes.all()
    serializer = WarehouseSerializer(warehouses, many=True)
    return Response(serializer.data)

  def post(self, request):
    """ criar um novo galpão/warehouse"""
    serializer = WarehouseSerializer(data=request.data)
    if serializer.is_valid():
      warehouse = Warehouse(**serializer.validated_data, created_by=request.user_uid).save()
      return Response(
        WarehouseSerializer(warehouse).data,
        status=status.HTTP_201_CREATED
      )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WarehouseDetailView(APIView):
  # permission_classes = [IsFirebaseAuthenticated] # Removido para usar o decorador
  @firebase_auth_required
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)
  
  def get(self, request, uid):
    """ Detalhes de um galpão/warehouse específico """
    try:
      warehouse = Warehouse.nodes.get(uid=uid)
      serializer = WarehouseSerializer(warehouse)
      return Response(serializer.data)
    except Warehouse.DoesNotExist:
      return Response(
        {'error': 'Galpão não encontrado'}, status=status.HTTP_404_NOT_FOUND
      )
      
class ProductListCreateView(APIView):
  # permission_classes = [IsFirebaseAuthenticated] # Removido para usar o decorador
  @firebase_auth_required
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)
  def get(self, request):
    """ listar os produtos """
    products = Product.nodes.all()
    data = []
    for product in products:
      product_data = ProductSerializer(product).data 
      # adicionar localização se existir:
      location = product.location.single()
      if location:
        product_data['location_code'] = location.code 
      data.append(product_data) 
    return Response(data)
  
  def post(self, request):
    """ criar um novo produto """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
      product = Product(
        sku=serializer.validated_data['sku'],
        name=serializer.validated_data['name'],
        quantity=serializer.validated_data('quantity', 0),
        unit=serializer.validated_data('unit', 'UN'),
      ).save()
      
      # Se localização foi fornecida, criar relacionamento
      location_code = serializer.validated_data.get('location_code')
      if location_code:
        try:
          bin_location = Bin.nodes.get(code=location_code)
          product.location.connect(bin_location)
        except Bin.DoesNotExist:
          pass
        
      return Response(
        ProductSerializer(product).data,
        status=status.HTTP_201_CREATED
      )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class HealthCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        """Health check endpoint"""
        return Response({
            'status': 'healthy',
            'service': 'WMS Graph API',
            'neo4j': 'connected'
        })