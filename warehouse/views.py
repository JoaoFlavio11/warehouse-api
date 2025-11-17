from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Warehouse, Bin, Product
from .serializers import WarehouseSerializer, ProductSerializer


class WarehouseListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        warehouses = Warehouse.nodes.all()
        data = []
        for w in warehouses:
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
                "address": getattr(w, "addres", ""),
                "capacity": getattr(w, "total_capacity", 0),
                "occupancy": occupancy,
            })

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            warehouse = Warehouse(
                name=serializer.validated_data["name"],
                addres=serializer.validated_data.get("address", ""),
                total_capacity=serializer.validated_data.get("capacity", 0),
                created_by="dev_user",
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
    permission_classes = [AllowAny]

    def get_object(self, uid):
        try:
            return Warehouse.nodes.get(uid=uid)
        except Warehouse.DoesNotExist:
            return None

    def get(self, request, uid):
        w = self.get_object(uid)
        if not w:
            return Response({"error": "Galpão não encontrado"}, status=404)

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

    # ✅ PERMITE DELETE
    def delete(self, request, uid):
        w = self.get_object(uid)
        if not w:
            return Response({"error": "Galpão não encontrado"}, status=404)

        w.delete()
        return Response({"message": "Galpão removido com sucesso"}, status=200)

    # (OPCIONAL) PERMITE UPDATE via PUT
    def put(self, request, uid):
        w = self.get_object(uid)
        if not w:
            return Response({"error": "Galpão não encontrado"}, status=404)

        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            w.name = serializer.validated_data["name"]
            w.addres = serializer.validated_data.get("address", "")
            w.total_capacity = serializer.validated_data.get("capacity", 0)
            w.save()

            return Response({"message": "Galpão atualizado com sucesso"}, status=200)
        return Response(serializer.errors, status=400)
