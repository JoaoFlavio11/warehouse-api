#orders/serializres
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.Serializer):
    """Serializer para itens do pedido"""
    uid = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    picked_quantity = serializers.IntegerField(read_only=True)
    bin_code = serializers.CharField(read_only=True, allow_null=True)


class OrderSerializer(serializers.Serializer):
    """Serializer para pedidos"""
    uid = serializers.CharField(read_only=True)
    order_number = serializers.CharField(required=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    items = OrderItemSerializer(many=True, required=False)

    def create(self, validated_data):
        """Criar novo pedido"""
        items_data = validated_data.pop('items', [])
        
        order = Order(
            order_number=validated_data['order_number'],
            status='pending'
        ).save()

        for item_data in items_data:
            order_item = OrderItem(
                product_sku=item_data['product_sku'],
                quantity=item_data['quantity']
            ).save()
            order.items.connect(order_item)

        return order
