# core/views.py
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer

# ... outras views ...

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para criar, listar, ver, atualizar e deletar pedidos.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Se precisar de autenticação, adicione a permission class aqui
    # permission_classes = [IsAuthenticated] # Exemplo com permissões do DRF
