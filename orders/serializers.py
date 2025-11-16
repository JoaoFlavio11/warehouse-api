from rest_framework import serializers
from .models import Order, OrderItem
from datetime import datetime


class OrderItemSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    picked_quantity = serializers.IntegerField(read_only=True)
    bin_code = serializers.CharField(read_only=True, allow_null=True)


class OrderSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    order_number = serializers.CharField(required=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    items = OrderItemSerializer(many=True, required=False)

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Carrega itens conectados no Neo4j
        items = instance.items.all()
        rep['items'] = OrderItemSerializer(items, many=True).data

        return rep

    def to_internal_value(self, data):
        mutable = dict(data)

        # Mapeando externalId -> order_number
        if 'externalId' in mutable and 'order_number' not in mutable:
            mutable['order_number'] = mutable.pop('externalId')

        # Corrigindo itens
        items = mutable.get('items')
        if isinstance(items, list):
            new_items = []
            for it in items:
                it = dict(it)
                if 'sku' in it:
                    it['product_sku'] = it.pop('sku')
                if 'qty' in it:
                    it['quantity'] = it.pop('qty')
                if 'pickedQty' in it:
                    it['picked_quantity'] = it.pop('pickedQty')
                new_items.append(it)
            mutable['items'] = new_items

        # Agora chama validação normal
        return super().to_internal_value(mutable)

    def create(self, validated_data):
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

    def update(self, instance, validated_data):
        status = validated_data.get("status")
        if status:
            instance.status = status
            if status == "completed":
                instance.completed_at = datetime.utcnow()

        instance.save()
        return instance
