from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsFirebaseAuthenticated
from .models import Order, OrderItem
from .serializers import OrderSerializer
from warehouse.models import Product
from routing.graph_algorithms import WarehouseGraph

"""
class OrderCreateView(APIView):
    """Criar pedido e sugerir rota de picking"""

    permission_classes = [IsFirebaseAuthenticated]

    def post(self, request):
        """
        Body esperado:
          {
            "order_number": "ORD-001",
            "warehouse_uid": "uuid",
            "items": [
              {"sku": "PROD-001", "quantity": 5},
              {"sku": "PROD-002", "quantity": 3}
            ]}
        """

        order_number = request.data.get("order_number")
        warehouse_uid = request.data.get("warehouse_uid")
        items = request.data.get("items", [])

        if not all([order_number, warehouse_uid, items]):
            return Response(
                {"error": "Dados incompletos"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Criar order
            order = Order(order_number=order_number, status="pending").save()

            # Localizar produtos e sugerir bins
            bin_codes = []
            order_items_data = []

            for item in items:
                sku = item["sku"]
                quantity = item["quantity"]

                # Buscar produto
                product = Product.nodes.get(sku=sku)
                location = product.location.single()

                if location and product.quantity >= quantity:
                    bin_code = location.code
                    bin_codes.append(bin_code)

                    # Criar order item
                    order_item = OrderItem(
                        product_sku=sku, quantity=quantity, bin_code=bin_code
                    ).save()
                    order.items.connect(order_item)

                    order_items_data.append(
                        {"sku": sku, "quantity": quantity, "bin_code": bin_code}
                    )
                else:
                    return Response(
                        {"error": f"Produto {sku} indisponível"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Calcular rota ótima
            graph = WarehouseGraph(warehouse_uid)
            optimal_route = graph.find_optimal_picking_route(bin_codes)

            return Response(
                {
                    "success": True,
                    "order_uid": order.uid,
                    "order_number": order.order_number,
                    "status": order.status,
                    "items": order_items_data,
                    "suggested_route": optimal_route,
                }, status=status.HTTP_201_CREATED, )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
"""

class OrderListView(APIView):
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        # ... código para listar pedidos
        orders = Order.nodes.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request): # <-- Adicionar este método
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Lógica de criação do pedido (ajuste conforme seu modelo)
            order = Order(**serializer.validated_data).save() 
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """ Listar pedidos """
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        orders = Order.nodes.all()
        data = []

        for order in orders:
            items = []

            for item in order.item.all():
                items.append({
                    'sku': item.product_sku,
                    'quantity': item.quantity,
                    'picked': item.picked_quantity,
                    'bin_code': item.bin_code
                })

            data.append({
                'uid': order.uid,
                'order_number': order.order_number,
                'status': order.status,
                'created_at': order.created_at,
                'items': items
            })

        return Response(data)