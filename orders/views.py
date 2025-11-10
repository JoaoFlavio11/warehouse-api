from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import Order
from .serializers import OrderSerializer

class OrderListView(generics.ListAPIView):
    """Listar todos os pedidos"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # <-- Adicionado

    def get_queryset(self):
        return Order.nodes.all()

    def list(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data)


class OrderCreateView(APIView):
    """Criar novo pedido"""
    permission_classes = [permissions.AllowAny]  # <-- Adicionado

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
