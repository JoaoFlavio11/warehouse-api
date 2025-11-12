# analytics/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from neo4j import GraphDatabase
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# ============================================================
# Conexão persistente com o Neo4j
# ============================================================
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "wms_password_123")  # mesma senha do exemplo que funciona

driver = GraphDatabase.driver(URI, auth=AUTH)


@method_decorator(csrf_exempt, name='dispatch')
class AnalyticsView(APIView):
    """Retorna métricas gerais do grafo Neo4j."""

    permission_classes = []  # rota pública

    def get(self, request):
        try:
            with driver.session() as session:
                # Conta total de nós e relacionamentos
                result_nodes = session.run("MATCH (n) RETURN count(n) AS totalNodes")
                result_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS totalRels")

                total_nodes = result_nodes.single()["totalNodes"]
                total_rels = result_rels.single()["totalRels"]

            return Response(
                {
                    "status": "ok",
                    "analytics": {
                        "total_nodes": total_nodes,
                        "total_relationships": total_rels,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao consultar o Neo4j: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
