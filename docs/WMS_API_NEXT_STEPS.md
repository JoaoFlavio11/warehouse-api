# 🚀 Próximos Passos - Desenvolvimento WMS API

## Fase 8: Algoritmos de Routing com NetworkX

### Objetivo
Implementar algoritmos de grafo para otimizar rotas de picking no warehouse.

### Passo 23: Criar routing/graph_algorithms.py

```python
import networkx as nx
from typing import List, Dict, Tuple
from warehouse.models import Warehouse, Zone, Aisle, Shelf, Bin

class WarehouseGraph:
    """
    Classe para construir e manipular o grafo do warehouse
    """
    def __init__(self, warehouse_uid: str):
        self.warehouse_uid = warehouse_uid
        self.graph = nx.Graph()
        self._build_graph()
    
    def _build_graph(self):
        """
        Constrói o grafo com base na estrutura do warehouse no Neo4j
        """
        # Buscar warehouse
        from warehouse.models import Warehouse
        warehouse = Warehouse.nodes.get(uid=self.warehouse_uid)
        
        # Adicionar nós para cada bin
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
        
        # Adicionar arestas (conexões entre bins)
        self._add_edges_by_proximity()
    
    def _add_edges_by_proximity(self):
        """
        Adiciona arestas entre bins próximos
        Lógica: bins no mesmo corredor têm peso menor
        """
        nodes = list(self.graph.nodes())
        
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                # Calcular "distância" baseada no código do bin
                # Ex: A-01-02-A e A-01-03-A são próximos
                distance = self._calculate_distance(node1, node2)
                if distance > 0:  # Se estão conectados
                    self.graph.add_edge(node1, node2, weight=distance)
    
    def _calculate_distance(self, bin1: str, bin2: str) -> float:
        """
        Calcula distância entre dois bins baseado no código
        Formato: CORREDOR-PRATELEIRA-NIVEL-POSICAO (Ex: A-01-02-A)
        """
        try:
            parts1 = bin1.split('-')
            parts2 = bin2.split('-')
            
            aisle1, shelf1, level1, pos1 = parts1
            aisle2, shelf2, level2, pos2 = parts2
            
            # Mesma prateleira
            if aisle1 == aisle2 and shelf1 == shelf2:
                # Diferença de níveis
                return abs(int(level1) - int(level2)) * 0.5
            
            # Mesmo corredor
            if aisle1 == aisle2:
                # Diferença de prateleiras
                return abs(int(shelf1) - int(shelf2)) * 2.0
            
            # Corredores diferentes - mais distante
            return abs(ord(aisle1) - ord(aisle2)) * 10.0
            
        except:
            return 0  # Não conectados
    
    def find_optimal_picking_route(self, bin_codes: List[str]) -> Dict:
        """
        Encontra a rota ótima para coletar items de múltiplos bins
        Usa algoritmo do Caixeiro Viajante aproximado
        """
        if not bin_codes:
            return {'route': [], 'total_distance': 0}
        
        # Subgrafo apenas com os bins necessários
        subgraph = self.graph.subgraph(bin_codes)
        
        # Se apenas um bin, retornar direto
        if len(bin_codes) == 1:
            return {
                'route': bin_codes,
                'total_distance': 0,
                'steps': [{'from': 'START', 'to': bin_codes[0], 'distance': 0}]
            }
        
        # Algoritmo aproximado para TSP
        route = self._approximate_tsp(subgraph, bin_codes)
        
        # Calcular distância total
        total_distance = 0
        steps = []
        for i in range(len(route) - 1):
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
        
        return {
            'route': route,
            'total_distance': round(total_distance, 2),
            'steps': steps,
            'bins_count': len(route)
        }
    
    def _approximate_tsp(self, graph: nx.Graph, nodes: List[str]) -> List[str]:
        """
        Algoritmo aproximado para Traveling Salesman Problem
        Usa estratégia greedy: sempre vai para o nó mais próximo ainda não visitado
        """
        if not nodes:
            return []
        
        # Começar do primeiro nó
        route = [nodes[0]]
        unvisited = set(nodes[1:])
        
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
        """
        Encontra o caminho mais curto entre dois bins
        """
        try:
            path = nx.shortest_path(
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
    
    def get_nearest_available_bins(self, product_sku: str, quantity: int) -> List[Dict]:
        """
        Encontra os bins mais próximos que contêm um produto específico
        """
        from warehouse.models import Product
        
        # Buscar produto
        try:
            products = Product.nodes.filter(sku=product_sku)
            available_bins = []
            
            for product in products:
                for bin_node in product.location.all():
                    if product.quantity > 0:
                        available_bins.append({
                            'bin_code': bin_node.code,
                            'quantity': product.quantity,
                            'available_space': bin_node.capacity - bin_node.occupied
                        })
            
            return sorted(available_bins, key=lambda x: x['quantity'], reverse=True)
        
        except Product.DoesNotExist:
            return []
```

### Passo 24: Criar routing/views.py

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsFirebaseAuthenticated
from .graph_algorithms import WarehouseGraph

class OptimalPickingRouteView(APIView):
    """
    Calcula a rota ótima de picking para um pedido
    """
    permission_classes = [IsFirebaseAuthenticated]
    
    def post(self, request):
        """
        Body esperado:
        {
            "warehouse_uid": "uuid-do-warehouse",
            "bin_codes": ["A-01-02-A", "B-03-01-B", "A-02-04-C"]
        }
        """
        warehouse_uid = request.data.get('warehouse_uid')
        bin_codes = request.data.get('bin_codes', [])
        
        if not warehouse_uid or not bin_codes:
            return Response(
                {'error': 'warehouse_uid e bin_codes são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            graph = WarehouseGraph(warehouse_uid)
            route = graph.find_optimal_picking_route(bin_codes)
            
            return Response({
                'success': True,
                'route': route,
                'optimization': 'TSP approximation algorithm'
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ShortestPathView(APIView):
    """
    Encontra o caminho mais curto entre dois bins
    """
    permission_classes = [IsFirebaseAuthenticated]
    
    def post(self, request):
        """
        Body esperado:
        {
            "warehouse_uid": "uuid",
            "start_bin": "A-01-02-A",
            "end_bin": "B-03-01-B"
        }
        """
        warehouse_uid = request.data.get('warehouse_uid')
        start_bin = request.data.get('start_bin')
        end_bin = request.data.get('end_bin')
        
        if not all([warehouse_uid, start_bin, end_bin]):
            return Response(
                {'error': 'Todos os campos são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            graph = WarehouseGraph(warehouse_uid)
            path = graph.find_shortest_path(start_bin, end_bin)
            
            return Response({
                'success': True,
                'path': path
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### Passo 25: Criar routing/urls.py

```python
from django.urls import path
from .views import OptimalPickingRouteView, ShortestPathView

urlpatterns = [
    path('picking-route/', OptimalPickingRouteView.as_view(), name='picking-route'),
    path('shortest-path/', ShortestPathView.as_view(), name='shortest-path'),
]
```

### Passo 26: Atualizar config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('warehouse.urls')),
    path('api/routing/', include('routing.urls')),  # Nova linha
]
```

---

## Fase 9: Orders Management

### Passo 27: Criar orders/models.py

```python
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
    """Pedido de separação"""
    uid = UniqueIdProperty()
    order_number = StringProperty(required=True, unique_index=True)
    status = StringProperty(choices={
        'pending': 'Pendente',
        'picking': 'Em Separação',
        'completed': 'Completo',
        'cancelled': 'Cancelado'
    }, default='pending')
    created_at = DateTimeProperty(default=datetime.utcnow)
    completed_at = DateTimeProperty()
    
    # Relacionamentos
    items = RelationshipTo('OrderItem', 'HAS_ITEM')

class OrderItem(StructuredNode):
    """Item do pedido"""
    uid = UniqueIdProperty()
    product_sku = StringProperty(required=True)
    quantity = IntegerProperty(required=True)
    picked_quantity = IntegerProperty(default=0)
    bin_code = StringProperty()  # Localização sugerida para picking
    
    order = RelationshipTo('Order', 'BELONGS_TO')
```

### Passo 28: Criar orders/views.py

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsFirebaseAuthenticated
from .models import Order, OrderItem
from warehouse.models import Product
from routing.graph_algorithms import WarehouseGraph

class OrderCreateView(APIView):
    """
    Criar pedido e sugerir rota de picking
    """
    permission_classes = [IsFirebaseAuthenticated]
    
    def post(self, request):
        """
        Body esperado:
        {
            "order_number": "ORD-001",
            "warehouse_uid": "uuid",
            "items": [
                {"sku": "PROD-001", "quantity": 5},
                {"sku": "PROD-002", "quantity": 3}
            ]
        }
        """
        order_number = request.data.get('order_number')
        warehouse_uid = request.data.get('warehouse_uid')
        items = request.data.get('items', [])
        
        if not all([order_number, warehouse_uid, items]):
            return Response(
                {'error': 'Dados incompletos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Criar order
            order = Order(
                order_number=order_number,
                status='pending'
            ).save()
            
            # Localizar produtos e sugerir bins
            bin_codes = []
            order_items_data = []
            
            for item in items:
                sku = item['sku']
                quantity = item['quantity']
                
                # Buscar produto
                product = Product.nodes.get(sku=sku)
                location = product.location.single()
                
                if location and product.quantity >= quantity:
                    bin_code = location.code
                    bin_codes.append(bin_code)
                    
                    # Criar order item
                    order_item = OrderItem(
                        product_sku=sku,
                        quantity=quantity,
                        bin_code=bin_code
                    ).save()
                    order.items.connect(order_item)
                    
                    order_items_data.append({
                        'sku': sku,
                        'quantity': quantity,
                        'bin_code': bin_code
                    })
                else:
                    return Response(
                        {'error': f'Produto {sku} indisponível'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Calcular rota ótima
            graph = WarehouseGraph(warehouse_uid)
            optimal_route = graph.find_optimal_picking_route(bin_codes)
            
            return Response({
                'success': True,
                'order_uid': order.uid,
                'order_number': order.order_number,
                'status': order.status,
                'items': order_items_data,
                'suggested_route': optimal_route
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrderListView(APIView):
    """Listar pedidos"""
    permission_classes = [IsFirebaseAuthenticated]
    
    def get(self, request):
        orders = Order.nodes.all()
        data = []
        
        for order in orders:
            items = []
            for item in order.items.all():
                items.append({
                    'sku': item.product_sku,
                    'quantity': item.quantity,
                    'picked': item.picked_quantity,
                    'bin_code': item.bin_code
                })
            
            data.append({
                'uid': order.uid,
                'order_number': order.order_number,
                'status': order.status,
                'created_at': order.created_at,
                'items': items
            })
        
        return Response(data)
```

### Passo 29: Criar orders/urls.py

```python
from django.urls import path
from .views import OrderCreateView, OrderListView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
]
```

### Passo 30: Atualizar config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('warehouse.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/orders/', include('orders.urls')),  # Nova linha
]
```

---

## Fase 10: Scripts de Dados de Teste

### Passo 31: Criar scripts/seed_warehouse.py

```python
"""
Script para popular o Neo4j com dados de teste
Execute: python manage.py shell < scripts/seed_warehouse.py
"""

from warehouse.models import Warehouse, Zone, Aisle, Shelf, Bin, Product

def seed_data():
    print("🌱 Iniciando seed do warehouse...")
    
    # Criar warehouse
    warehouse = Warehouse(
        name="Centro de Distribuição SP",
        address="Av. Industrial, 1000 - São Paulo, SP",
        total_capacity=10000.0
    ).save()
    print(f"✅ Warehouse criado: {warehouse.name}")
    
    # Criar zonas
    zones = [
        ('Recebimento', 'receiving'),
        ('Armazenagem A', 'storage'),
        ('Separação', 'picking'),
        ('Expedição', 'shipping')
    ]
    
    for zone_name, zone_type in zones:
        zone = Zone(name=zone_name, zone_type=zone_type).save()
        warehouse.zones.connect(zone)
        print(f"✅ Zona criada: {zone_name}")
        
        # Criar corredores (apenas na zona de armazenagem)
        if zone_type == 'storage':
            for aisle_code in ['A', 'B', 'C']:
                aisle = Aisle(code=aisle_code).save()
                zone.aisles.connect(aisle)
                
                # Criar prateleiras
                for shelf_num in range(1, 6):  # 5 prateleiras
                    shelf_code = f"{shelf_num:02d}"
                    shelf = Shelf(code=shelf_code, levels=4).save()
                    aisle.shelves.connect(shelf)
                    
                    # Criar bins
                    for level in range(1, 5):  # 4 níveis
                        for position in ['A', 'B']:  # 2 posições por nível
                            bin_code = f"{aisle_code}-{shelf_code}-{level:02d}-{position}"
                            bin_node = Bin(
                                code=bin_code,
                                capacity=100.0,
                                occupied=0.0
                            ).save()
                            shelf.bins.connect(bin_node)
    
    print(f"✅ Total de bins criados: {len(Bin.nodes.all())}")
    
    # Criar produtos
    products = [
        ('PROD-001', 'Notebook Dell', 50, 'UN'),
        ('PROD-002', 'Mouse Logitech', 200, 'UN'),
        ('PROD-003', 'Teclado Mecânico', 100, 'UN'),
        ('PROD-004', 'Monitor 24"', 75, 'UN'),
        ('PROD-005', 'Webcam HD', 150, 'UN'),
    ]
    
    bins = list(Bin.nodes.all())
    
    for i, (sku, name, qty, unit) in enumerate(products):
        product = Product(
            sku=sku,
            name=name,
            quantity=qty,
            unit=unit
        ).save()
        
        # Alocar em um bin
        if i < len(bins):
            bin_node = bins[i]
            product.location.connect(bin_node)
            bin_node.occupied = qty
            bin_node.save()
            print(f"✅ Produto criado: {name} em {bin_node.code}")
    
    print("🎉 Seed completo!")

if __name__ == "__main__":
    seed_data()
```

---

## 🔗 Fase 11: Integração com Next.js

### Passo 32: Criar API client no Next.js

Crie `lib/wms-api.ts` no projeto Next.js:

```typescript
import { getAuth } from 'firebase/auth';

const WMS_API_BASE_URL = process.env.NEXT_PUBLIC_WMS_API_URL || 'http://localhost:8000/api';

async function getAuthToken(): Promise<string | null> {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) return null;
  return await user.getIdToken();
}

export const wmsApi = {
  async getWarehouses() {
    const token = await getAuthToken();
    const response = await fetch(`${WMS_API_BASE_URL}/warehouses/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.json();
  },

  async getProducts() {
    const token = await getAuthToken();
    const response = await fetch(`${WMS_API_BASE_URL}/products/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.json();
  },

  async createOrder(data: {
    order_number: string;
    warehouse_uid: string;
    items: Array<{ sku: string; quantity: number }>;
  }) {
    const token = await getAuthToken();
    const response = await fetch(`${WMS_API_BASE_URL}/orders/create/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async getOptimalRoute(data: {
    warehouse_uid: string;
    bin_codes: string[];
  }) {
    const token = await getAuthToken();
    const response = await fetch(`${WMS_API_BASE_URL}/routing/picking-route/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
};
```

### Passo 33: Adicionar .env.local no Next.js

```env
NEXT_PUBLIC_WMS_API_URL=http://localhost:8000/api
```

---

## 📊 Fase 12: Testes e Validação

### Comandos úteis:

```bash
# Rodar servidor Django
python manage.py runserver

# Popular banco com dados de teste
python manage.py shell < scripts/seed_warehouse.py

# Ver logs do Neo4j
docker logs wms-neo4j -f

# Acessar shell do Neo4j
docker exec -it wms-neo4j cypher-shell -u neo4j -p wms_password_123

# Limpar dados do Neo4j (cuidado!)
# No cypher-shell:
MATCH (n) DETACH DELETE n;
```

---

## 🚀 Fase 13: Deploy

### Opção 1: Railway

1. Criar conta no Railway
2. Conectar repositório GitHub
3. Adicionar Neo4j como plugin
4. Configurar variáveis de ambiente
5. Deploy automático

### Opção 2: Google Cloud Run

```bash
# Build da imagem Docker
docker build -t wms-api .

# Push para Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/wms-api

# Deploy no Cloud Run
gcloud run deploy wms-api \
  --image gcr.io/PROJECT_ID/wms-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📈 Melhorias Futuras

1. **Cache com Redis**
   - Cache de rotas frequentes
   - Cache de consultas de produtos

2. **WebSockets para Tempo Real**
   - Atualizar status de pedidos em tempo real
   - Notificações de estoque baixo

3. **Machine Learning**
   - Previsão de demanda
   - Otimização de layout do warehouse

4. **Analytics**
   - Dashboard de performance
   - Métricas de picking time
   - Heatmap de áreas mais acessadas

---

**Me avise quando concluir cada fase para continuarmos juntos!** 🚀
