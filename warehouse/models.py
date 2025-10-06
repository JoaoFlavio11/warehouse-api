from neomodel import(
  StructuredNode, 
  StringProperty, 
  IntegerProperty,
  FloatProperty,
  RelationshipTo,
  RelationshipFrom,
  UniqueIdProperty,
  DateTimeProperty
)
from datetime import datetime

class Warehouse(StructuredNode):
  """ classe p/ galpão """
  uid = UniqueIdProperty()
  name = StringProperty(required=True, unique_index=True)
  addres = StringProperty()
  total_capacity = FloatProperty(default=0.0)
  created_at = DateTimeProperty(default=datetime.utcnow)
  
  #relacionamentos:
  zones = RelationshipTo('Zone', 'CONTAINS')

class Zone(StructuredNode):
  """ classe p/ zona dentro do galpão (ex: Recebimento, Expedição) """
  uid = UniqueIdProperty()
  name= StringProperty(required=True)
  zone_type = StringProperty(choices={
    'receiving': 'Recebimento',
    'storage': 'Armazenagem',
    'picking': 'Separação',
    'shipping': 'Expedição',
  })
  
  #Relacionamentos
  warehouse = RelationshipFrom('Warehouse', 'CONTAINS')
  aisles = RelationshipTo('Aisle', 'CONTAINS')
  
class Aisle(StructuredNode):
  """ classe p/ corredor dentro de uma zona """
  uid = UniqueIdProperty()
  code = StringProperty(required=True) #ex: a, b
  
  #Relacionamentos
  zone = RelationshipFrom('Zone', 'CONTAINS')
  shelves = RelationshipFrom('Shelf', 'CONTAINS')

class Shelf(StructuredNode):
  """ Prateleira """
  uid = UniqueIdProperty()
  code = StringProperty(required=True)  # Ex: 01, 02, 03
  levels = IntegerProperty(default=4)  # níveis
  
  #Relacionamentos
  aisle = RelationshipFrom('Aisle', 'CONTAINS')
  bins = RelationshipFrom('Bin', 'CONTAINS')
  
class Bin(StructuredNode):
    """(bin/box) para armazenar produtos"""
    uid = UniqueIdProperty()
    code = StringProperty(required=True, unique_index=True)  # Ex: A-01-03-B (Corredor-Prateleira-Nível-Posição)
    capacity = FloatProperty(default=100.0)  # Capacidade em unidades
    occupied = FloatProperty(default=0.0)
    
    shelf = RelationshipFrom('Shelf', 'CONTAINS')
    products = RelationshipFrom('Product', 'STORED_IN')

class Product(StructuredNode):
    """Produto armazenado"""
    uid = UniqueIdProperty()
    sku = StringProperty(required=True, unique_index=True)
    name = StringProperty(required=True)
    quantity = IntegerProperty(default=0)
    unit = StringProperty(default='UN')  # UN, KG, L, etc
    
    location = RelationshipTo('Bin', 'STORED_IN')