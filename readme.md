# 📦 WMS Graph API - Warehouse Management System

Sistema de gerenciamento de armazém baseado em grafos, desenvolvido com Django, Neo4j e algoritmos de otimização de rotas.

## 📚 Documentação

Este projeto possui guias completos para desenvolvimento:

### 🎯 Guias Principais

1. **[WMS_API_SETUP_GUIDE.md](./WMS_API_SETUP_GUIDE.md)**
   - Setup completo do ambiente
   - Configuração de Firebase, Django e Neo4j
   - Estrutura base do projeto
   - Primeiros endpoints e autenticação
   - **Comece por aqui!**

2. **[WMS_API_NEXT_STEPS.md](./WMS_API_NEXT_STEPS.md)**
   - Algoritmos de grafo com NetworkX
   - Sistema de Orders/Pedidos
   - Otimização de rotas de picking
   - Integração com Next.js
   - Scripts de seed e testes
   - Deploy e melhorias futuras

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                     │
│                    + Firebase Auth                       │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP + Bearer Token
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Django REST API (Python)                    │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Firebase Auth Middleware                         │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────┐  ┌──────────┐  ┌─────────┐  ┌───────┐ │
│  │ Warehouse │  │Inventory │  │ Routing │  │Orders │ │
│  │   Module  │  │  Module  │  │ Module  │  │Module │ │
│  └───────────┘  └──────────┘  └─────────┘  └───────┘ │
│         │              │            │            │      │
│         └──────────────┴────────────┴────────────┘      │
│                        │                                 │
│              ┌─────────▼──────────┐                     │
│              │   Neomodel OGM     │                     │
│              └─────────┬──────────┘                     │
└────────────────────────┼────────────────────────────────┘
                         │ Bolt Protocol
                         ▼
           ┌─────────────────────────────┐
           │      Neo4j Graph Database    │
           │                              │
           │  Nodes:                      │
           │  • Warehouse                 │
           │  • Zone                      │
           │  • Aisle                     │
           │  • Shelf                     │
           │  • Bin                       │
           │  • Product                   │
           │  • Order                     │
           │                              │
           │  Relationships:              │
           │  • CONTAINS                  │
           │  • STORED_IN                 │
           │  • LOCATED_AT                │
           │  • HAS_ITEM                  │
           └─────────────────────────────┘
```

---

## 🎯 Funcionalidades Principais

### ✅ Gerenciamento de Warehouse
- Criar e gerenciar múltiplos armazéns
- Organização hierárquica: Warehouse → Zone → Aisle → Shelf → Bin
- Controle de capacidade e ocupação

### ✅ Inventário
- Registro de produtos com SKU único
- Rastreamento de localização por bin
- Controle de quantidade disponível

### ✅ Otimização de Rotas
- Algoritmo TSP (Traveling Salesman Problem) para picking
- Caminho mais curto entre bins (Dijkstra)
- Grafo ponderado baseado na estrutura física do warehouse

### ✅ Gestão de Pedidos
- Criação de pedidos com múltiplos items
- Sugestão automática de rota ótima de separação
- Rastreamento de status (pending, picking, completed)

### ✅ Segurança
- Autenticação via Firebase tokens
- Middleware de validação em todas as rotas
- CORS configurado para frontend

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| **Backend Framework** | Django | 5.0+ |
| **API** | Django REST Framework | 3.14+ |
| **Banco de Grafos** | Neo4j | 5.15+ |
| **OGM** | Neomodel | 5.2+ |
| **Algoritmos** | NetworkX | 3.2+ |
| **Autenticação** | Firebase Admin SDK | 6.3+ |
| **Linguagem** | Python | 3.11+ |
| **Containerização** | Docker | - |

---

## 📦 Estrutura do Projeto

```
wms-graph-api/
├── config/                    # Configurações Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # Auth e middlewares
│   ├── firebase_auth.py
│   ├── middleware.py
│   └── permissions.py
├── warehouse/                 # Módulo de warehouse
│   ├── models.py             # Warehouse, Zone, Aisle, Shelf, Bin, Product
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── inventory/                 # Módulo de inventário
├── routing/                   # Algoritmos de grafo
│   ├── graph_algorithms.py   # NetworkX + TSP
│   ├── views.py
│   └── urls.py
├── orders/                    # Gestão de pedidos
│   ├── models.py             # Order, OrderItem
│   ├── views.py
│   └── urls.py
├── scripts/                   # Scripts utilitários
│   └── seed_warehouse.py     # Popular dados de teste
├── docker-compose.yml         # Neo4j local
├── requirements.txt
├── .env
├── .gitignore
└── manage.py
```

---

## 🚀 Quick Start

```bash
# 1. Clonar e entrar no diretório
git clone https://github.com/SEU_USUARIO/wms-graph-api.git
cd wms-graph-api

# 2. Criar e ativar virtualenv
python -m venv venv
source venv/bin/activate  # Mac/Linux
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Iniciar Neo4j
docker-compose up -d

# 5. Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# 6. Migrações Django
python manage.py migrate

# 7. Popular dados de teste
python manage.py shell < scripts/seed_warehouse.py

# 8. Rodar servidor
python manage.py runserver
```

Acesse:
- API: http://localhost:8000/api/
- Neo4j Browser: http://localhost:7474

---

## 📖 Endpoints Principais

### Warehouse
```http
GET    /api/warehouses/           # Listar warehouses
POST   /api/warehouses/           # Criar warehouse
GET    /api/warehouses/{uid}/     # Detalhes
```

### Products
```http
GET    /api/products/             # Listar produtos
POST   /api/products/             # Criar produto
```

### Routing
```http
POST   /api/routing/picking-route/    # Rota ótima de picking
POST   /api/routing/shortest-path/    # Caminho mais curto
```

### Orders
```http
GET    /api/orders/               # Listar pedidos
POST   /api/orders/create/        # Criar pedido + rota
```

### Health
```http
GET    /api/health/               # Status da API
```

---

## 🔐 Autenticação

Todas as rotas (exceto `/health/`) exigem token Firebase:

```bash
curl -X GET http://localhost:8000/api/warehouses/ \
  -H "Authorization: Bearer SEU_TOKEN_FIREBASE"
```

No Next.js:
```typescript
import { getAuth } from 'firebase/auth';

const auth = getAuth();
const user = auth.currentUser;
const token = await user?.getIdToken();

// Usar token nas requisições
```

---

## 🧪 Desenvolvimento

### Comandos Úteis

```bash
# Rodar servidor em modo debug
python manage.py runserver 0.0.0.0:8000

# Shell Django
python manage.py shell

# Criar novo app
python manage.py startapp nome_app

# Ver logs Neo4j
docker logs wms-neo4j -f

# Limpar dados Neo4j
docker exec -it wms-neo4j cypher-shell -u neo4j -p wms_password_123
# No cypher: MATCH (n) DETACH DELETE n;
```

### Exemplo de Query Cypher

```cypher
// Ver estrutura do warehouse
MATCH (w:Warehouse)-[r*]->(b:Bin)
RETURN w, r, b
LIMIT 50

// Produtos e localizações
MATCH (p:Product)-[:STORED_IN]->(b:Bin)
RETURN p.sku, p.name, b.code, p.quantity

// Contar bins por corredor
MATCH (a:Aisle)-[:CONTAINS*]->(b:Bin)
RETURN a.code, count(b) as bins_count
ORDER BY bins_count DESC
```

---

## 🧬 Modelo de Grafo

### Nodes (Nós)

```python
Warehouse
  ├── Zone (receiving, storage, picking, shipping)
  │    └── Aisle (A, B, C, ...)
  │         └── Shelf (01, 02, 03, ...)
  │              └── Bin (A-01-02-A)
  │
  └── Product (SKU único)

Order
  └── OrderItem
```

### Relationships (Relacionamentos)

```
Warehouse -[CONTAINS]-> Zone
Zone -[CONTAINS]-> Aisle
Aisle -[CONTAINS]-> Shelf
Shelf -[CONTAINS]-> Bin
Product -[STORED_IN]-> Bin
Order -[HAS_ITEM]-> OrderItem
```

---

## 🎓 Conceitos de Algoritmos

### TSP (Traveling Salesman Problem)
- **Objetivo**: Encontrar a rota mais curta visitando todos os bins
- **Algoritmo**: Greedy approximation (sempre vai ao mais próximo)
- **Uso**: Otimização de picking de pedidos

### Dijkstra / A*
- **Objetivo**: Caminho mais curto entre dois pontos
- **Uso**: Navegação individual entre bins

### Grafo Ponderado
- **Pesos**: Calculados pela distância física entre bins
- **Lógica**: 
  - Mesma prateleira = peso 0.5
  - Mesmo corredor = peso 2.0
  - Corredores diferentes = peso 10.0

---

## 📊 Exemplo de Uso

### 1. Criar Warehouse

```bash
curl -X POST http://localhost:8000/api/warehouses/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CD São Paulo",
    "address": "Av. Industrial, 1000",
    "total_capacity": 10000
  }'
```

### 2. Criar Produto

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-001",
    "name": "Notebook Dell",
    "quantity": 50,
    "unit": "UN",
    "location_code": "A-01-02-A"
  }'
```

### 3. Criar Pedido com Rota Otimizada

```bash
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-001",
    "warehouse_uid": "WAREHOUSE_UID",
    "items": [
      {"sku": "PROD-001", "quantity": 5},
      {"sku": "PROD-002", "quantity": 3}
    ]
  }'
```

**Resposta:**
```json
{
  "success": true,
  "order_uid": "...",
  "order_number": "ORD-001",
  "status": "pending",
  "items": [...],
  "suggested_route": {
    "route": ["A-01-02-A", "B-03-01-B"],
    "total_distance": 12.5,
    "steps": [
      {"from": "A-01-02-A", "to": "B-03-01-B", "distance": 12.5}
    ],
    "bins_count": 2
  }
}
```

---

## 🐛 Troubleshooting

### Neo4j não conecta
```bash
# Verificar se está rodando
docker ps | grep neo4j

# Ver logs
docker logs wms-neo4j

# Reiniciar
docker-compose restart neo4j
```

### Erro de autenticação Firebase
- Verificar se `firebase-service-account.json` está correto
- Confirmar path no `.env`
- Testar token no https://jwt.io

### CORS error
- Adicionar origin no `CORS_ALLOWED_ORIGINS`
- Verificar se `corsheaders` está em `INSTALLED_APPS`

---

## 📈 Roadmap

- [x] Setup base Django + Neo4j
- [x] Autenticação Firebase
- [x] CRUD Warehouse/Products
- [x] Algoritmos de routing
- [x] Sistema de Orders
- [ ] Cache com Redis
- [ ] WebSockets tempo real
- [ ] Dashboard analytics
- [ ] Machine Learning para previsão
- [ ] Deploy production

---

## 📄 Licença

MIT License - Sinta-se livre para usar em projetos pessoais e comerciais.

---

**Desenvolvido com Django, Neo4j e algoritmos de grafos**
