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
    id = serializers.CharField(source="uid", read_only=True)
    externalId = serializers.CharField(source="order_number", required=False, allow_blank=True)
    status = serializers.CharField(read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    completedAt = serializers.DateTimeField(source="completed_at", read_only=True, allow_null=True)

    items = OrderItemSerializer(many=True, required=False)

    def to_internal_value(self, data):
        mutable = dict(data)

        # Renomear externalId -> order_number
        if "externalId" in mutable:
            mutable["order_number"] = mutable.pop("externalId")

        # Converter itens vindo do frontend
        if "items" in mutable:
            items = []
            for it in mutable["items"]:
                new_it = dict(it)
                # renomear campos
                if "sku" in new_it:
                    new_it["product_sku"] = new_it.pop("sku")
                if "qty" in new_it:
                    new_it["quantity"] = new_it.pop("qty")
                if "pickedQty" in new_it:
                    new_it["picked_quantity"] = new_it.pop("pickedQty")
                items.append(new_it)
            mutable["items"] = items

        return super().to_internal_value(mutable)

    def create(self, validated_data):
        items = validated_data.pop("items", [])

        order_number = validated_data.get("order_number") or ""

        order = Order(
            order_number=order_number,
            status="pending",
        ).save()

        for item in items:
            order_item = OrderItem(
                product_sku=item["product_sku"],
                quantity=item["quantity"],
            ).save()
            order.items.connect(order_item)

        return order


    def update(self, instance, validated_data):
        if "status" in validated_data:
            instance.status = validated_data["status"]
            if instance.status == "completed":
                instance.completed_at = datetime.utcnow()

        instance.save()
        return instance
