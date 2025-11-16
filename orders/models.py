from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    RelationshipTo,
    UniqueIdProperty
)
from datetime import datetime


class Order(StructuredNode):
    uid = UniqueIdProperty()
    order_number = StringProperty(required=True, unique_index=True)

    status = StringProperty(
        choices={
            'pending': 'Pendente',
            'picking': 'Em Separação',
            'completed': 'Completo',
            'cancelled': 'Cancelado',
        },
        default='pending'
    )

    created_at = DateTimeProperty(default=datetime.utcnow)
    completed_at = DateTimeProperty()

    items = RelationshipTo('OrderItem', 'HAS_ITEM')


class OrderItem(StructuredNode):
    uid = UniqueIdProperty()
    product_sku = StringProperty(required=True)
    quantity = IntegerProperty(required=True)
    picked_quantity = IntegerProperty(default=0)
    bin_code = StringProperty()
    order = RelationshipTo('Order', 'BELONGS_TO')
