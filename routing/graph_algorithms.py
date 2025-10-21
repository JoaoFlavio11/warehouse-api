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
      self._add_edges_by_proximity()
    
    def _add_edges_by_proximity(self):
      """ Adiciona arestas entre bins próximos Lógica: bins no mesmo corredor têm peso menor """
      nodes = list(self.graph.nodes())
      
      for i, node1 in enumerate(nodes):
        for node2 in nodes[i+1:]:
          # Calcular "distância" baseada no código do bin
          # Ex: A-01-02-A e A-01-03-A são próximos
          distance = self._calculate_distance(node1, node2)
          if distance > 0: #se estão conectados:
            self.graph.add_edge(node1, node2, weight=distance)
    
    def _calculate_distance(self, bin1: str, bin2: str) -> float:
      """ Calcula distância entre dois bins baseado no código 
      Formato: CORREDOR-PRATELEIRA-NIVEL-POSICAO (Ex: A-01-02-A) 
      """
      try:
        parts1 = bin1.split('-')
        parts2 = bin2.split('-')
        
        aisle1, shelf1, level1, pos1 = parts1
        aisle2, shelf2, level2, pos2 = parts2
        
        #mesma prateleira:
        if aisle1 == aisle2 and shelf1 == shelf2:
          # diferença dos níveis
          return abs(int(level1) - int(level2)) * 0.5
        
        # Mesmo corredor
        if aisle1 == aisle2:
          # Diferença de prateleiras
          return abs(int(shelf1) - int(shelf2)) * 2.0
        
        # Corredores diferentes - mais distante
        return abs(ord(aisle1) - ord(aisle2)) * 10.0

      except:
        return 0 #não conectados
  
    def find_optional_picking_route(self, bin_codes: List[str]) -> Dict:
      """  Encontra a rota ótima para coletar items de múltiplos bins Usa algoritmo do Caixeiro Viajante aproximado """
      if not bin_codes:
        return {'route': [], 'total_distance': 0}
      
      # Subgrafo apenas com os bins necessários
      subgraph = self.graph.subgraph(bin_codes)
      
      #se apenas um BIN, retornar direto:
      if len(bin_codes) == 1:
        return {
          'route': bin_codes,
          'total_distance': 0,
          'steps': [{'from': 'START', 'to': bin_codes[0], 'distance': 0}]
        }
      
      # Algoritmo aproximado para TSP
      route = self._approximate_tsp(subgraph, bin_codes)
      
      # Calcular distancia total:
      total_distance = 0
      steps = []
      for i in range(len(route) -1 ):
        distance = nx.shortest_path_length(
          self.graph, 
          route[i], 
          route[i+1], 
          weight='weight'
        )
        total_distance += distance
        steps.append({
          'from': route[i],
          'to': route[i+1],
          'distance': round(distance, 2)
        })
        
        return{
          'route': route,
          'total_distance': round(total_distance, 2),
          'steps': steps,
          'bins_count': len(route)
        }
    
    def _approximate_tsp(self, graph: nx.Graph, nodes: List[str]) -> List[str]:
      """ Algoritmo aproximado para Traveling Salesman Problem - Usa estratégia greedy: sempre vai para o nó mais próximo ainda não visitado """
      if not nodes:
        return []
      
      #Começar no primeiro nó
      route = [nodes[0]]
      unvisited = set(nodes[1:i])
      
      current = nodes[0]
      
      while unvisited:
        # Encontrar nó mais próximo não visitado
        nearest = min(
          unvisited,
          key=lambda node: nx.shortest_path_length(
            self.graph, current, node, weight='weight'
          ) if nx.has_path(self.graph, current, node) else float('inf')
        )
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
      
      return route
    
    def find_shortest_path(self, start_bin: str, end_bin: str) -> Dict:
      """ Encontra o caminho mais curto entre dois bins """
      try:
        path: nx.shortest_path(
          self.graph, 
          start_bin, 
          end_bin, 
          weight='weight'
        )
        distance = nx.shortest_path_length(
          self.graph, 
          start_bin, 
          end_bin, 
          weight='weight'
        )
        return {
          'path': path,
          'distance': round(distance, 2),
          'steps': len(path) - 1
        }
      except nx.NetworkXNoPath:
        return {
          'error': 'Caminho não encontrado',
          'path': [],
          'distance': None
        }
    
    def get_nearest_avaliable_bins(self, product_sku: str, quantity: int) -> List[Dict]:
      """ Encontra os bins mais próximos que contêm um produto específico """
      from warehouse.models import Product
      
      #Buscar produto
      try:
        products = Product.nodes.filter(sku=product_sku)
        avaliable_bins = []
        
        for product on products:
          for bin_node in product.location.all():
            if product.quantity > 0: 
              avaliable_bins.append({
                'bin_code': bin_node.code,
                'quantity': product.quantity,
                'available_space': bin_node.capacity - bin_node.occupied
              })
        
        return sorted(available_bins, key=lambda x: x['quantity'], reverse=True)
      except Product.DoesNotExist:
        return [] 