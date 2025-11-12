from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # ✅ adicionado
from .models import Warehouse, Bin, Product
from .serializers import WarehouseSerializer, ProductSerializer


class WarehouseListCreateView(APIView):
    """Lista ou cria armazéns"""
    permission_classes = [AllowAny]  # ✅ público

    def get(self, request):
        """Listar todos os armazéns"""
        warehouses = Warehouse.nodes.all()
        data = []
        for w in warehouses:
            # cálculo de ocupação (soma dos bins conectados)
            total_capacity = 0
            total_occupied = 0
            for zone in w.zones:
                for aisle in zone.aisles:
                    for shelf in aisle.shelves:
                        for b in shelf.bins:
                            total_capacity += getattr(b, "capacity", 0) or 0
                            total_occupied += getattr(b, "occupied", 0) or 0

            occupancy = (
                round((total_occupied / total_capacity) * 100, 1)
                if total_capacity > 0 else 0
            )

            data.append({
                "id": w.uid,
                "name": w.name,
                "address": getattr(w, "addres", ""),  # modelo tem "addres"
                "capacity": getattr(w, "total_capacity", 0),
                "occupancy": occupancy,
            })

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """Criar um novo armazém"""
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            warehouse = Warehouse(
                name=serializer.validated_data["name"],
                addres=serializer.validated_data.get("address", ""),
                total_capacity=serializer.validated_data.get("capacity", 0),
                created_by="dev_user",  # mock temporário
            ).save()
            return Response({
                "id": warehouse.uid,
                "name": warehouse.name,
                "address": warehouse.addres,
                "capacity": warehouse.total_capacity,
                "occupancy": 0,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WarehouseDetailView(APIView):
    """Detalhar um armazém específico"""
    permission_classes = [AllowAny]  # ✅ público

    def get(self, request, uid):
        try:
            w = Warehouse.nodes.get(uid=uid)
            total_capacity = 0
            total_occupied = 0
            for zone in w.zones:
                for aisle in zone.aisles:
                    for shelf in aisle.shelves:
                        for b in shelf.bins:
                            total_capacity += getattr(b, "capacity", 0) or 0
                            total_occupied += getattr(b, "occupied", 0) or 0

            occupancy = (
                round((total_occupied / total_capacity) * 100, 1)
                if total_capacity > 0 else 0
            )

            data = {
                "id": w.uid,
                "name": w.name,
                "address": getattr(w, "addres", ""),
                "capacity": getattr(w, "total_capacity", 0),
                "occupancy": occupancy,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Warehouse.DoesNotExist:
            return Response({"error": "Galpão não encontrado"}, status=404)
