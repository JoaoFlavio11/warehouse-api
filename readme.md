<div align="center">

# 📦 EasyRoute API
### Sistema de Gerenciamento de Armazém (WMS) com Banco de Grafos

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0%2B-092E20?style=for-the-badge&logo=django&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

![GitHub repo size](https://img.shields.io/github/repo-size/JoaoFlavio11/warehouse-api?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/JoaoFlavio11/warehouse-api?style=flat-square)
![GitHub license](https://img.shields.io/github/license/JoaoFlavio11/warehouse-api?style=flat-square)

</div>

---

## 📚 Sumário
- [🎯 Visão Geral](#-visão-geral-do-projeto)
- [🚀 Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [✨ Funcionalidades](#-funcionalidades)
- [🧬 Modelo de Grafo (Neo4j)](#-modelo-de-grafo-neo4j)
- [🛠️ Instalação e Configuração](#-instalação-e-configuração)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [📖 Endpoints Principais](#-endpoints-principais)
- [🔐 Autenticação](#-autenticação-firebase)

---

## 🎯 Visão Geral do Projeto

O **EasyRoute API** é o backend robusto do sistema EasyRoute, um WMS (*Warehouse Management System*) moderno e inteligente. Diferente dos sistemas tradicionais relacionais, utilizamos o poder dos **Bancos de Dados de Grafos (Neo4j)** para modelar a complexa hierarquia física de um armazém e otimizar rotas de coleta (*picking*).

**Principais capacidades:**
* Gerenciamento hierárquico (Warehouse → Zone → Aisle → Shelf → Bin).
* Controle de inventário com localização precisa.
* Roteirização otimizada utilizando algoritmos de grafos (caminho mais curto).
* Autenticação segura e escalável via Firebase.

---

## 🚀 Tecnologias Utilizadas

| Categoria | Tecnologia | Badge |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11+ | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) |
| **Framework Web** | Django 5.0+ | ![Django](https://img.shields.io/badge/-Django-092E20?logo=django&logoColor=white) |
| **API** | Django REST Framework | ![DRF](https://img.shields.io/badge/-DRF-a30f2d?logo=django&logoColor=white) |
| **Banco de Grafos** | Neo4j | ![Neo4j](https://img.shields.io/badge/-Neo4j-008CC1?logo=neo4j&logoColor=white) |
| **OGM** | Neomodel | ![Neomodel](https://img.shields.io/badge/-Neomodel-blue) |
| **Algoritmos** | NetworkX | ![NetworkX](https://img.shields.io/badge/-NetworkX-orange) |
| **Autenticação** | Firebase Admin SDK | ![Firebase](https://img.shields.io/badge/-Firebase-FFCA28?logo=firebase&logoColor=black) |
| **DevOps** | Docker + Docker Compose | ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white) |

---

## ✨ Funcionalidades

### 🏢 Estrutura do Armazém
Modelagem hierárquica completa:
> **Warehouse** (Armazém) ➔ **Zone** (Zona) ➔ **Aisle** (Corredor) ➔ **Shelf** (Prateleira) ➔ **Bin** (Caixa/Posição)

### 📦 Inventário Inteligente
* Cadastro de Produtos e SKUs.
* Rastreamento de quantidade em tempo real.
* Localização exata via relação `Product -[:STORED_IN]-> Bin`.

### 🧾 Pedidos e Rotas
* Criação de pedidos multi-itens.
---

## 🧬 Modelo de Grafo (Neo4j)

Abaixo está a representação visual da modelagem dos nós e relacionamentos no Neo4j:

```mermaid
graph TD
    W[Warehouse] -->|CONTAINS| Z[Zone]
    Z -->|CONTAINS| A[Aisle]
    A -->|CONTAINS| S[Shelf]
    S -->|CONTAINS| B[Bin]
    P[Product] -->|STORED_IN| B
    O[Order] -->|HAS_ITEM| OI[OrderItem]
    
    classDef container fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef item fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    
    class W,Z,A,S,B container;
    class P,O,OI item;

```
-----

## 🛠️ Instalação e Configuração

### Pré-requisitos

  * Docker & Docker Compose
  * Python 3.11+

### Passo a Passo

1.  **Clone o repositório**

    ```bash
    git clone [https://github.com/JoaoFlavio11/warehouse-api](https://github.com/JoaoFlavio11/warehouse-api)
    cd warehouse-api
    ```

2.  **Configure as variáveis de ambiente**
    Crie um arquivo `.env` na raiz do projeto:

    ```ini
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=wms_password_123

    # Caminho para sua chave privada do Firebase
    FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
    ```

3.  **Inicie o Neo4j via Docker**

    ```bash
    docker-compose up -d neo4j
    ```

    > Acesse o painel do Neo4j em: [http://localhost:7474](https://www.google.com/search?q=http://localhost:7474)

4.  **Instale as dependências locais**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Popule o banco com dados de teste (Seed)**

    ```bash
    python manage.py shell < scripts/seed_warehouse.py
    ```

6.  **Inicie o servidor**

    ```bash
    python manage.py runserver
    ```

-----

## 📂 Estrutura do Projeto

```plaintext
warehouse-api/
├── config/             # Configurações globais do Django
├── core/               # Middleware e Autenticação Firebase
├── warehouse/          # Modelagem da estrutura física (Nós e Relacionamentos)
├── products/           # Gestão de Inventário
├── orders/             # Lógica de Pedidos e Algoritmos de Rota
├── dashboard/          # Métricas e Analytics
├── lib/                # Utilitários e Algoritmos de Grafos Puros
├── scripts/            # Scripts de Seed e automação
├── docker-compose.yml
└── manage.py
```

-----

## 📖 Endpoints Principais

### 📦 Warehouses

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/warehouses/` | Lista todos os armazéns |
| `POST` | `/api/warehouses/` | Cria um novo armazém |
| `GET` | `/api/warehouses/{uid}/` | Detalhes da hierarquia do armazém |

### 📦 Produtos

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/products/` | Listagem de inventário |
| `POST` | `/api/products/` | Cadastro de SKU |

### 🧾 Pedidos & Rotas

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/orders/create/` | Cria pedido e gera rota otimizada |
| `GET` | `/api/orders/` | Histórico de pedidos |

-----

## 🔐 Autenticação (Firebase)

O sistema utiliza tokens JWT do Firebase. Todas as requisições protegidas devem incluir o cabeçalho:

```http
Authorization: Bearer <SEU_TOKEN_JWT_FIREBASE>
```

**Exemplo com cURL:**

```bash
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6..."
```
-----
<div align="center">
  Desenvolvido por João Flavio - Unisal 2025
</div>
