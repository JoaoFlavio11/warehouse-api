# 📦 EasyRoute API: Sistema de Gerenciamento de Armazém (WMS) com Grafos

## 🎯 Visão Geral do Projeto

O **EasyRoute API** é o *backend* do **_EasyRoute_**, um Sistema de Gerenciamento de Armazém (WMS), focado em fornecer uma solução robusta e eficiente para a gestão de inventário, pedidos e a estrutura física do armazém.

O diferencial deste projeto reside na utilização de um **Banco de Dados de Grafos (Neo4j)** para modelar a estrutura do armazém e as relações de inventário.

## 🚀 Tecnologias Utilizadas

O projeto é construído sobre uma *stack* Python robusta, com foco em escalabilidade e facilidade de desenvolvimento:

| Categoria | Tecnologia | Versão | Descrição |
| :--- | :--- | :--- | :--- |
| **Linguagem** | **Python** | 3.x | Linguagem principal de desenvolvimento. |
| **Framework Web** | **Django** | 5.0.1 | Framework de alto nível para desenvolvimento rápido e seguro. |
| **API** | **Django REST Framework** | 3.14.0 | Toolkit flexível para construção de APIs web. |
| **Banco de Dados** | **Neo4j** | 5.15 (Docker) | Banco de dados de grafos para modelagem da estrutura do armazém. |
| **Integração Neo4j** | **neomodel** | 5.2.1 | Biblioteca Python para modelagem de objetos no Neo4j. |
| **Autenticação** | **firebase-admin** | 6.3.0 | Integração com Firebase para validação de tokens de autenticação. |
| **Grafos** | **networkx** | 3.2.1 | Biblioteca para criação, manipulação e estudo da estrutura, dinâmica e funções de redes complexas. |

## ✨ Funcionalidades Principais

O sistema oferece as seguintes funcionalidades através de endpoints RESTful:

### 1. Gerenciamento de Estrutura do Armazém
*   **Modelagem Hierárquica:** Criação e gestão de armazéns, zonas, corredores (*aisles*), prateleiras (*shelves*) e *bins* (localizações de armazenamento).
*   **Controle de Capacidade:** Rastreamento da ocupação e capacidade de cada *bin*.

### 2. Inventário e Produtos
*   Registro de produtos com SKU único.
*   Rastreamento da localização exata do produto (Bin) e quantidade disponível.

### 3. Gestão de Pedidos e Otimização
*   Criação e rastreamento de pedidos e seus itens.

### 4. Segurança
*   **Autenticação:** Validação de usuários via tokens JWT do **Firebase Authentication**.
*   **CORS:** Configuração de *Cross-Origin Resource Sharing* para integração segura com o *frontend*.

## 🧬 Modelo de Grafo (Neo4j)

A estrutura do armazém é modelada como um grafo, onde os nós (Nodes) representam as entidades e os relacionamentos (Relationships) definem a hierarquia e a localização.

| Tipo | Nó (Node) | Relacionamento (Relationship) |
| :--- | :--- | :--- |
| **Estrutura** | `Warehouse`, `Zone`, `Aisle`, `Shelf`, `Bin` | `CONTAINS` (e.g., `Warehouse -[CONTAINS]-> Zone`) |
| **Inventário** | `Product` | `STORED_IN` (e.g., `Product -[STORED_IN]-> Bin`) |
| **Pedidos** | `Order`, `OrderItem` | `HAS_ITEM` (e.g., `Order -[HAS_ITEM]-> OrderItem`) |

### Exemplo de Query Cypher para Rastreamento

```cypher
// Produtos e localizações
MATCH (p:Product)-[:STORED_IN]->(b:Bin)<-[:CONTAINS]-(s:Shelf)<-[:CONTAINS]-(a:Aisle)
RETURN p.sku, p.name, b.code, a.code, s.code, p.quantity
```

## 🛠️ Configuração e Instalação

Para rodar a API localmente, é altamente recomendado o uso do Docker para o banco de dados Neo4j.

### Pré-requisitos

*   **Python** (versão 3.x)
*   **pip** (gerenciador de pacotes Python)
*   **Docker** e **Docker Compose**

### 1. Clonar o Repositório

```bash
git clone https://github.com/JoaoFlavio11/warehouse-api.git
cd warehouse-api
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto. Este arquivo deve conter as credenciais de acesso ao Neo4j e as configurações do Firebase.

```env
# Configurações do Neo4j (devem corresponder ao docker-compose.yml)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=wms_password_123

# Configurações do Firebase Admin SDK
# (Necessário para validar tokens de autenticação do frontend)
# Consulte a documentação do Firebase Admin SDK para obter o arquivo JSON de credenciais.
# Exemplo: FIREBASE_CREDENTIALS_PATH=/caminho/para/seu/serviceAccountKey.json
FIREBASE_CREDENTIALS_PATH=
```

### 3. Iniciar o Banco de Dados Neo4j (Docker)

O `docker-compose.yml` já está configurado para iniciar o Neo4j na porta `7687` (Bolt) e `7474` (Browser).

```bash
docker-compose up -d neo4j
```

Você pode acessar o Neo4j Browser em `http://localhost:7474` com as credenciais `neo4j` / `wms_password_123`.

### 4. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 5. Popular Dados de Teste (Opcional)

Para iniciar com uma estrutura de armazém e dados de exemplo, execute o script de *seeding*:

```bash
python manage.py shell < scripts/seed_warehouse.py
```

### 6. Rodar a API

Inicie o servidor de desenvolvimento do Django:

```bash
python manage.py runserver 0.0.0.0:8000
```

A API estará acessível em `http://localhost:8000`.

## 📄 Estrutura de Pastas

A estrutura do projeto segue o padrão Django, com módulos separados por funcionalidade:

```
warehouse-api/
├── config/             # Configurações globais do Django
├── core/               # Lógica central (Autenticação, Middlewares, Permissões)
├── dashboard/          # Módulo de Dashboard (endpoints de métricas)
├── lib/                # Bibliotecas e utilitários (ex: lógica de grafos)
├── orders/             # Módulo de Gestão de Pedidos
├── products/           # Módulo de Produtos
├── reports/            # Módulo de Relatórios
├── scripts/            # Scripts utilitários (ex: seed_warehouse.py)
├── warehouse/          # Módulo de Estrutura do Armazém (Warehouse, Zone, Bin, etc.)
├── docker-compose.yml  # Configuração do Neo4j
├── requirements.txt    # Dependências Python
└── manage.py           # Utilitário de linha de comando do Django
```
