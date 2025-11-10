#products/views
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from neo4j import GraphDatabase

# Configure sua conexão com Neo4j
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "wms_password_123")  # substitua pela sua senha
driver = GraphDatabase.driver(URI, auth=AUTH)


@method_decorator(csrf_exempt, name='dispatch')
class ProductListCreateView(View):
    """
    GET  -> Lista todos os produtos
    POST -> Cria um novo produto
    """

    def get(self, request):
        with driver.session() as session:
            result = session.run("MATCH (p:Product) RETURN p ORDER BY p.name ASC")
            products = [dict(record["p"]) for record in result]
        return JsonResponse(products, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name')
            description = data.get('description', '')
            price = data.get('price', 0)
            stock = data.get('current_stock', 0)

            with driver.session() as session:
                session.run(
                    """
                    CREATE (p:Product {
                        id: randomUUID(),
                        name: $name,
                        description: $description,
                        price: $price,
                        current_stock: $stock
                    })
                    """,
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                )

            return JsonResponse({"message": "Produto criado com sucesso"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailView(View):
    """
    GET    -> Retorna um produto pelo ID
    PUT    -> Atualiza um produto existente
    DELETE -> Remove um produto
    """

    def get(self, request, product_id):
        with driver.session() as session:
            result = session.run(
                "MATCH (p:Product {id: $id}) RETURN p", id=product_id
            ).single()
            if not result:
                return JsonResponse({"error": "Produto não encontrado"}, status=404)
            return JsonResponse(dict(result["p"]))

    def put(self, request, product_id):
        try:
            data = json.loads(request.body.decode('utf-8'))
            with driver.session() as session:
                session.run(
                    """
                    MATCH (p:Product {id: $id})
                    SET p.name = $name,
                        p.description = $description,
                        p.price = $price,
                        p.current_stock = $stock
                    """,
                    id=product_id,
                    name=data.get('name'),
                    description=data.get('description'),
                    price=data.get('price'),
                    stock=data.get('current_stock', 0),
                )
            return JsonResponse({"message": "Produto atualizado com sucesso"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, product_id):
        with driver.session() as session:
            session.run("MATCH (p:Product {id: $id}) DETACH DELETE p", id=product_id)
        return JsonResponse({"message": "Produto deletado com sucesso"})
