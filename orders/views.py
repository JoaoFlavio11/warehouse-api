from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django.http import Http404
from .models import Order
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Order.nodes.all()

    def list(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        print("Serializer errors on create:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        obj = Order.nodes.get_or_none(uid=self.kwargs.get("pk"))
        if obj is None:
            raise Http404("Pedido não encontrado.")
        return obj

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        return Response(OrderSerializer(order).data)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(OrderSerializer(updated).data)

        print("Serializer errors on update:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
