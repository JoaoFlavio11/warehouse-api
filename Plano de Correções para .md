# 🛠️ Plano de Correções para `warehouse-api`

**Autor:** Manus AI
**Data:** 05 de Novembro de 2025
**Objetivo:** Corrigir os erros de roteamento (404, URL duplicada), autenticação (500) e métodos HTTP (405) para garantir o funcionamento correto da API.

---

## 📝 Resumo dos Problemas Identificados

Com base nos logs de erro (`pasted_content.txt`) e na análise do código-fonte do repositório, os seguintes problemas foram confirmados:

| ID | Problema | Status HTTP | Arquivos Afetados | Causa Principal |
| :---: | :--- | :---: | :--- | :--- |
| **1** | URL Duplicada (`/api/api/...`) | 404 | `config/urls.py` | Inclusão de `api/` em excesso no roteamento principal. |
| **2** | Erro de Autenticação Firebase | 500 | `core/firebase_auth.py`, `core/permissions.py` | Uso incorreto do decorator de autenticação em `APIView`s. |
| **3** | Método Não Permitido (`/api/orders/`) | 405 | `orders/views.py` | A `OrderListView` não implementa o método `POST`. |
| **4** | Rotas Faltantes (`/api/routes/`, `/api/dashboard/stats/`) | 404 | `routing/urls.py`, `warehouse/urls.py` | Endpoints não registrados ou registrados incorretamente. |

---

## 🚀 Trilha de Correções Detalhadas

Siga os passos abaixo na ordem para aplicar as correções.

### Passo 1: Corrigir o Roteamento Principal (Problema 1 e 4)

O problema de URL duplicada (`/api/api/`) e as rotas faltantes (`/api/routes/`, `/api/dashboard/stats/`) estão relacionados à forma como as URLs são incluídas.

#### 1.1. Editar `config/urls.py`

Este arquivo está correto, pois define o prefixo `/api/` para cada aplicação.

```python
# warehouse-api/config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('warehouse.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/orders/', include('orders.urls')),
]
```

#### 1.2. Editar `warehouse/urls.py` (Adicionar rota `dashboard/stats/`)

O endpoint `/api/dashboard/stats/` está faltando. Assumindo que ele deve estar na aplicação `warehouse` (junto com `warehouses/` e `products/`).

**Ação:** Adicione a rota `dashboard/stats/` e importe a view correspondente.

```python
# warehouse-api/warehouse/urls.py
from django.urls import path
from .views import (
  WarehouseListCreateView,
  WarehouseDetailView, 
  ProductListCreateView,
  HealthCheckView,
  DashboardStatsView # <-- Adicionar esta importação
)

urlpatterns = [
  path('health/', HealthCheckView.as_view(), name='health-check'),  
  path('warehouses/', WarehouseListCreateView.as_view(), name='warehouse-list'),
  path('warehouses/<str:uid>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
  path('products/', ProductListCreateView.as_view(), name='product-list'),
  path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'), # <-- Adicionar esta linha
]
```

> **Nota:** Você precisará criar a classe `DashboardStatsView` em `warehouse/views.py` se ela ainda não existir.

#### 1.3. Editar `routing/urls.py` (Corrigir rota `routes/`)

O log mostra um erro 404 para `/api/routes/`. O arquivo `routing/urls.py` define as rotas `picking-route/` e `shortest-path/`.

**Ação:** Se o frontend espera `/api/routes/`, você deve adicionar uma view para essa URL ou verificar se o frontend está chamando o endpoint correto.

**Opção 1 (Se `/api/routes/` deve listar rotas):** Adicione uma view em `routing/views.py` e registre-a:
```python
# Exemplo em routing/urls.py
# ...
from .views import OptimalPickingRouteView, ShortestPathView, RouteListView # <-- Adicionar RouteListView

urlpatterns = [
  path('', RouteListView.as_view(), name='route-list'), # <-- Adicionar esta linha para /api/routes/
  path('picking-route/', OptimalPickingRouteView.as_view(), name='picking-route'),
  path('shortest-path/', ShortestPathView.as_view(), name='shortest-path'),
]
```

### Passo 2: Corrigir o Erro de Autenticação (Problema 2)

O erro `AttributeError: 'ProductListCreateView' object has no attribute 'META'` ocorre porque o decorator `@firebase_auth_required` (que não está no repositório, mas é referenciado pelo erro) está sendo aplicado incorretamente em `APIView`s.

O seu código já usa a classe `IsFirebaseAuthenticated` em `warehouse/views.py`, o que é a abordagem correta do Django REST Framework (DRF). O erro 500 sugere que o middleware ou a classe de permissão está falhando ao obter o usuário.

O problema é que a classe `IsFirebaseAuthenticated` em `core/permissions.py` espera que o `request` já tenha o atributo `firebase_user` definido.

```python
# warehouse-api/core/permissions.py
# ...
  def has_permission(self, request, view):
    return request.firebase_user is not None # <-- Depende de um middleware/decorator
```

**Ação:** Implementar um **Middleware** para processar o token Firebase e anexar o usuário ao objeto `request` antes que a permissão seja verificada.

#### 2.1. Criar `core/middleware.py`

Crie o arquivo `core/middleware.py` e adicione o seguinte código:

```python
# warehouse-api/core/middleware.py
from django.http import JsonResponse
from core.firebase_auth import verify_firebase_token

class FirebaseAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.firebase_user = None
        
        # Ignorar autenticação para rotas de admin ou health check
        if request.path.startswith('/admin/') or request.path.endswith('/health/'):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            user_data = verify_firebase_token(token)
            
            if user_data:
                request.firebase_user = user_data
            else:
                # Opcional: Retornar 401 se o token for inválido, mas estiver presente
                # Se você usar a classe de permissão, ela cuidará disso.
                pass 

        response = self.get_response(request)
        return response
```

#### 2.2. Atualizar `config/settings.py`

Adicione o novo middleware na lista `MIDDLEWARE`:

```python
# warehouse-api/config/settings.py
# ...
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ... outros middlewares
    'core.middleware.FirebaseAuthenticationMiddleware', # <-- Adicionar esta linha
    # ...
]
```

> **Explicação:** O middleware irá garantir que, para qualquer requisição, o atributo `request.firebase_user` seja preenchido (se o token for válido) ou seja `None` (se não houver token ou for inválido). A classe `IsFirebaseAuthenticated` agora funcionará corretamente.

### Passo 3: Permitir Criação de Pedidos (Problema 3)

O erro `Method Not Allowed: /api/orders/` (405) ocorre porque a `OrderListView` em `orders/views.py` não permite requisições `POST`.

**Ação:** Mudar a view para permitir `POST` ou usar a `OrderCreateView` que já existe.

O arquivo `orders/urls.py` já tem:
```python
# warehouse-api/orders/urls.py
# ...
urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
]
```

Se o frontend está enviando `POST` para `/api/orders/`, ele deveria estar enviando para `/api/orders/create/`.

**Recomendação:** Se o frontend não puder ser alterado para usar `/api/orders/create/`, você deve adicionar o método `post` à `OrderListView`.

#### 3.1. Editar `orders/views.py`

**Ação:** Adicione o método `post` à `OrderListView` para que ela possa lidar com a criação de pedidos.

```python
# warehouse-api/orders/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from core.permissions import IsFirebaseAuthenticated # Assumindo que você usa a permissão

class OrderListView(APIView):
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        # ... código para listar pedidos
        orders = Order.nodes.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request): # <-- Adicionar este método
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Lógica de criação do pedido (ajuste conforme seu modelo)
            order = Order(**serializer.validated_data).save() 
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Remova OrderCreateView se você consolidar a lógica acima.
# Se mantiver OrderCreateView, o frontend deve usar /api/orders/create/
```

---

## ✅ Checklist de Implementação

Execute as seguintes ações no seu projeto:

1.  **Criação de View:** Crie a classe `DashboardStatsView` em `warehouse/views.py` (se não existir).
2.  **Passo 1:** Edite `warehouse/urls.py` e adicione a rota `dashboard/stats/`.
3.  **Passo 1:** Edite `routing/urls.py` para incluir a `RouteListView` (se necessário).
4.  **Passo 2:** Crie o arquivo `core/middleware.py` com o código fornecido.
5.  **Passo 2:** Edite `config/settings.py` e adicione `'core.middleware.FirebaseAuthenticationMiddleware'` à lista `MIDDLEWARE`.
6.  **Passo 3:** Edite `orders/views.py` e adicione o método `post` à `OrderListView`.
7.  **Teste Final:** Reinicie o servidor Django (`python manage.py runserver 8000`) e teste todas as rotas que estavam falhando:
    *   `GET /api/warehouses/` (Deve funcionar, sem `/api/api/`)
    *   `GET /api/products/` (Deve funcionar, sem erro 500)
    *   `POST /api/orders/` (Deve funcionar, sem erro 405)
    *   `GET /api/routes/` (Deve funcionar, sem erro 404)
    *   `GET /api/dashboard/stats/` (Deve funcionar, sem erro 404)
