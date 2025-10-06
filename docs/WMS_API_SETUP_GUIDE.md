# Guia de Setup - API WMS com Django + Neo4j

## 📋 Pré-requisitos

- Python 3.11+
- Docker Desktop (para Neo4j local)
- Git
- Firebase Project (já configurado no Next.js)

---

## 🚀 Fase 1: Setup Inicial do Projeto

### Passo 1: Criar o Repositório

```bash
# Criar novo diretório
mkdir wms-graph-api
cd wms-graph-api

# Inicializar git
git init
git branch -M main

# Criar repositório no GitHub e conectar
git remote add origin https://github.com/SEU_USUARIO/wms-graph-api.git
```

### Passo 2: Configurar Ambiente Virtual Python

```bash
# Criar virtualenv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate
```

### Passo 3: Criar requirements.txt

Crie o arquivo `requirements.txt` na raiz:

```txt
Django==5.0.1
djangorestframework==3.14.0
neomodel==5.2.1
firebase-admin==6.3.0
django-cors-headers==4.3.1
python-dotenv==1.0.0
gunicorn==21.2.0
networkx==3.2.1
```

### Passo 4: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 5: Criar Projeto Django

```bash
django-admin startproject config .
```

### Passo 6: Configurar Neo4j com Docker

Crie `docker-compose.yml` na raiz:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15
    container_name: wms-neo4j
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/wms_password_123
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

Iniciar Neo4j:

```bash
docker-compose up -d
```

Acesse: http://localhost:7474 (user: neo4j, password: wms_password_123)

### Passo 7: Configurar Variáveis de Ambiente

Crie `.env` na raiz:

```env
# Django
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Neo4j
NEO4J_BOLT_URL=bolt://neo4j:wms_password_123@localhost:7687

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Passo 8: Baixar Credenciais do Firebase

1. Acesse: https://console.firebase.google.com
2. Selecione seu projeto
3. Vá em: **Project Settings** > **Service Accounts**
4. Clique em: **Generate New Private Key**
5. Salve como `firebase-service-account.json` na raiz do projeto

⚠️ **IMPORTANTE**: Adicione ao `.gitignore`:

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# Django
*.log
db.sqlite3
media/
staticfiles/

# Environment
.env
firebase-service-account.json

# Neo4j
neo4j_data/
neo4j_logs/

# IDEs
.vscode/
.idea/
*.swp
*.swo
```

---

## 🏗️ Fase 2: Estrutura Base do Projeto

### Passo 9: Criar Apps Django

```bash
python manage.py startapp core
python manage.py startapp warehouse
python manage.py startapp inventory
python manage.py startapp routing
python manage.py startapp orders
```

Estrutura final:

```
wms-graph-api/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── firebase_auth.py
│   └── middleware.py
├── warehouse/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── inventory/
├── routing/
├── orders/
├── docker-compose.yml
├── requirements.txt
├── .env
├── .gitignore
└── manage.py
```

---

## ⚙️ Fase 3: Configuração do Django

### Passo 10: Configurar config/settings.py

Adicione/modifique as seguintes seções:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'django_neomodel',
    
    # Local apps
    'core',
    'warehouse',
    'inventory',
    'routing',
    'orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.FirebaseAuthenticationMiddleware',
]

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# Neo4j
NEOMODEL_NEO4J_BOLT_URL = os.getenv('NEO4J_BOLT_URL')

# Firebase
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (SQLite para admin Django, Neo4j para dados WMS)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## 🔐 Fase 4: Autenticação Firebase

### Passo 11: Criar core/firebase_auth.py

```python
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
import os

# Inicializar Firebase Admin
def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")

initialize_firebase()

def verify_firebase_token(token):
    """
    Verifica token do Firebase e retorna dados do usuário
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'email_verified': decoded_token.get('email_verified', False),
        }
    except Exception as e:
        return None
```

### Passo 12: Criar core/middleware.py

```python
from django.utils.functional import SimpleLazyObject
from .firebase_auth import verify_firebase_token

class FirebaseAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.firebase_user = SimpleLazyObject(lambda: self._get_user(request))
        response = self.get_response(request)
        return response

    def _get_user(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            user_data = verify_firebase_token(token)
            return user_data
        
        return None
```

### Passo 13: Criar core/permissions.py

```python
from rest_framework import permissions

class IsFirebaseAuthenticated(permissions.BasePermission):
    """
    Permission para verificar se usuário está autenticado via Firebase
    """
    message = 'Autenticação Firebase obrigatória.'

    def has_permission(self, request, view):
        return request.firebase_user is not None
```

---

## 📊 Fase 5: Modelos de Grafo com Neomodel

### Passo 14: Criar warehouse/models.py

```python
from neomodel import (
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
    """Representa um armazém/warehouse"""
    uid = UniqueIdProperty()
    name = StringProperty(required=True, unique_index=True)
    address = StringProperty()
    total_capacity = FloatProperty(default=0.0)
    created_at = DateTimeProperty(default=datetime.utcnow)
    
    # Relacionamentos
    zones = RelationshipTo('Zone', 'CONTAINS')

class Zone(StructuredNode):
    """Zona dentro do warehouse (ex: Recebimento, Armazenagem, Expedição)"""
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    zone_type = StringProperty(choices={
        'receiving': 'Recebimento',
        'storage': 'Armazenagem',
        'picking': 'Separação',
        'shipping': 'Expedição',
    })
    
    warehouse = RelationshipFrom('Warehouse', 'CONTAINS')
    aisles = RelationshipTo('Aisle', 'CONTAINS')

class Aisle(StructuredNode):
    """Corredor dentro de uma zona"""
    uid = UniqueIdProperty()
    code = StringProperty(required=True)  # Ex: A, B, C
    
    zone = RelationshipFrom('Zone', 'CONTAINS')
    shelves = RelationshipTo('Shelf', 'CONTAINS')

class Shelf(StructuredNode):
    """Prateleira/estante no corredor"""
    uid = UniqueIdProperty()
    code = StringProperty(required=True)  # Ex: 01, 02, 03
    levels = IntegerProperty(default=4)  # Quantidade de níveis
    
    aisle = RelationshipFrom('Aisle', 'CONTAINS')
    bins = RelationshipTo('Bin', 'CONTAINS')

class Bin(StructuredNode):
    """Posição específica (bin/box) para armazenar produtos"""
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
```

### Passo 15: Criar warehouse/serializers.py

```python
from rest_framework import serializers

class WarehouseSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    address = serializers.CharField(required=False, allow_blank=True)
    total_capacity = serializers.FloatField(default=0.0)
    created_at = serializers.DateTimeField(read_only=True)

class ZoneSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    zone_type = serializers.ChoiceField(choices=['receiving', 'storage', 'picking', 'shipping'])

class ProductSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    sku = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    quantity = serializers.IntegerField(default=0)
    unit = serializers.CharField(max_length=10, default='UN')
    location_code = serializers.CharField(required=False, allow_blank=True)

class BinSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    code = serializers.CharField(max_length=50)
    capacity = serializers.FloatField(default=100.0)
    occupied = serializers.FloatField(default=0.0)
    available = serializers.SerializerMethodField()
    
    def get_available(self, obj):
        return obj.capacity - obj.occupied
```

---

## 🌐 Fase 6: Views e URLs

### Passo 16: Criar warehouse/views.py

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsFirebaseAuthenticated
from .models import Warehouse, Zone, Product, Bin
from .serializers import WarehouseSerializer, ZoneSerializer, ProductSerializer, BinSerializer

class WarehouseListCreateView(APIView):
    permission_classes = [IsFirebaseAuthenticated]
    
    def get(self, request):
        """Listar todos os warehouses"""
        warehouses = Warehouse.nodes.all()
        serializer = WarehouseSerializer(warehouses, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Criar novo warehouse"""
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            warehouse = Warehouse(**serializer.validated_data).save()
            return Response(
                WarehouseSerializer(warehouse).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WarehouseDetailView(APIView):
    permission_classes = [IsFirebaseAuthenticated]
    
    def get(self, request, uid):
        """Detalhes de um warehouse específico"""
        try:
            warehouse = Warehouse.nodes.get(uid=uid)
            serializer = WarehouseSerializer(warehouse)
            return Response(serializer.data)
        except Warehouse.DoesNotExist:
            return Response(
                {'error': 'Warehouse não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ProductListCreateView(APIView):
    permission_classes = [IsFirebaseAuthenticated]
    
    def get(self, request):
        """Listar todos os produtos"""
        products = Product.nodes.all()
        data = []
        for product in products:
            product_data = ProductSerializer(product).data
            # Adicionar localização se existir
            location = product.location.single()
            if location:
                product_data['location_code'] = location.code
            data.append(product_data)
        return Response(data)
    
    def post(self, request):
        """Criar novo produto"""
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = Product(
                sku=serializer.validated_data['sku'],
                name=serializer.validated_data['name'],
                quantity=serializer.validated_data.get('quantity', 0),
                unit=serializer.validated_data.get('unit', 'UN')
            ).save()
            
            # Se localização foi fornecida, criar relacionamento
            location_code = serializer.validated_data.get('location_code')
            if location_code:
                try:
                    bin_location = Bin.nodes.get(code=location_code)
                    product.location.connect(bin_location)
                except Bin.DoesNotExist:
                    pass
            
            return Response(
                ProductSerializer(product).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HealthCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        """Health check endpoint"""
        return Response({
            'status': 'healthy',
            'service': 'WMS Graph API',
            'neo4j': 'connected'
        })
```

### Passo 17: Criar warehouse/urls.py

```python
from django.urls import path
from .views import (
    WarehouseListCreateView,
    WarehouseDetailView,
    ProductListCreateView,
    HealthCheckView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('warehouses/', WarehouseListCreateView.as_view(), name='warehouse-list'),
    path('warehouses/<str:uid>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
    path('products/', ProductListCreateView.as_view(), name='product-list'),
]
```

### Passo 18: Configurar config/urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('warehouse.urls')),
]
```

---

## 🧪 Fase 7: Testar a API

### Passo 19: Aplicar Migrações Django

```bash
python manage.py makemigrations
python manage.py migrate
```

### Passo 20: Criar Superuser (Opcional)

```bash
python manage.py createsuperuser
```

### Passo 21: Iniciar Servidor

```bash
python manage.py runserver
```

Acesse: http://localhost:8000/api/health/

### Passo 22: Testar Endpoints com Firebase Token

No seu Next.js, pegue o token do usuário:

```typescript
import { getAuth } from 'firebase/auth';

const auth = getAuth();
const user = auth.currentUser;
const token = await user?.getIdToken();
```

Teste com cURL:

```bash
curl -X GET http://localhost:8000/api/warehouses/ \
  -H "Authorization: Bearer SEU_TOKEN_FIREBASE"
```

---

## 📝 Próximos Passos

Agora que o setup base está funcionando, podemos desenvolver:

1. ✅ **Endpoints de Inventory Management**
2. ✅ **Algoritmos de Routing com NetworkX**
3. ✅ **Order Processing**
4. ✅ **Otimização de Picking Routes**
5. ✅ **Integração completa com Next.js**

---

## 🐛 Troubleshooting

### Neo4j não conecta
```bash
# Ver logs do container
docker logs wms-neo4j

# Reiniciar
docker-compose restart neo4j
```

### Firebase credentials inválido
- Verifique se o arquivo JSON está na raiz
- Confirme que o path no .env está correto

### CORS error no Next.js
- Verifique se o origin está em CORS_ALLOWED_ORIGINS
- Confirme que corsheaders está em INSTALLED_APPS

---

## 🎯 Checklist de Conclusão da Fase 1

- [ ] Repositório criado e conectado ao GitHub
- [ ] Python virtualenv ativo
- [ ] Django instalado e projeto criado
- [ ] Neo4j rodando no Docker
- [ ] Firebase credentials configurado
- [ ] Apps criados (warehouse, inventory, routing, orders)
- [ ] Middleware de autenticação funcionando
- [ ] Endpoints básicos respondendo
- [ ] Health check retornando 200

**Quando terminar esta fase, me avise para continuarmos com os algoritmos de grafo!**
