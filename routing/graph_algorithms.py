  import networkx as nx 
  from typing import List, Dict, Tuple
  from warehouse.models import Warehouse, Zoe, Aisle, Shelf, Bin
  
  class WarehouseGraph:
    """ Classe para construir e manipular o grafo do warehouse """
    def __init__(self, warehouse_uid: str):
      self.warehouse_uid = warehouse_uid
      self.graph = nx.Graph()
      self.build_graph
    
    def _build_graph(self):
      """ Constrói o grafo com base na estrutura do warehouse no Neo4j """
      # Buscando o Warehouse
      from warehouse.models import Warehouse
      warehouse = Warehouse.nodes.get(uid=self.warehouse_uid)
      
      # Adicioar o nó para cada bin
      for zone in warehouse.zones.all():
        for aisle in zone.aisles.all():
          for shelf in aisle.shelves.all():
            for bin_node in shelf.bins.all():
              self.graph.add_node(
                  bin_node.code,
                  uid=bin_node.uid,
                  capacity=bin_node.capacity,
                  occupied=bin_node.occupied
                )
    
      # Adicionar arestas (conexão das bins)