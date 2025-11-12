# analytics/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from neo4j import GraphDatabase
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime

# ============================================================
# Conexão persistente com o Neo4j
# ============================================================
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "wms_password_123")

driver = GraphDatabase.driver(URI, auth=AUTH)


@method_decorator(csrf_exempt, name='dispatch')
class AnalyticsView(APIView):
    """Retorna métricas completas para o dashboard Analytics."""

    permission_classes = []

    def get(self, request):
        try:
            with driver.session() as session:
                # ===============================================
                # ORDERS
                # ===============================================
                query_orders = """
                MATCH (o:Order)
                OPTIONAL MATCH (o)-[:HAS_STATUS]->(s:Status)
                RETURN 
                    count(o) AS totalOrders,
                    collect(s.name) AS statuses
                """
                orders_result = session.run(query_orders).single()
                total_orders = orders_result["totalOrders"]
                statuses = [s for s in orders_result["statuses"] if s]

                # Conta por status
                by_status = {}
                for status_name in statuses:
                    by_status[status_name] = by_status.get(status_name, 0) + 1

                # Pedidos ao longo do tempo (últimos 30 dias)
                # Corrige: converte timestamp (Double/Integer) para data string
                query_period = """
                MATCH (o:Order)
                WHERE o.created_at IS NOT NULL
                RETURN o.created_at AS ts
                ORDER BY ts ASC
                LIMIT 200
                """
                period_results = session.run(query_period)
                by_period = []
                for record in period_results:
                    ts = record["ts"]
                    if isinstance(ts, (int, float)):
                        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    else:
                        date_str = str(ts)
                    # Conta acumulada por dia
                    existing = next((item for item in by_period if item["date"] == date_str), None)
                    if existing:
                        existing["count"] += 1
                    else:
                        by_period.append({"date": date_str, "count": 1})

                # ===============================================
                # PRODUCTS
                # ===============================================
                query_products = """
                MATCH (p:Product)
                OPTIONAL MATCH (p)-[:HAS_MOVEMENT]->(m:Movement)
                RETURN 
                    count(p) AS totalProducts,
                    count(m) AS totalMovements,
                    count { (p) WHERE p.current_stock <= 5 AND p.current_stock > 0 } AS lowStock,
                    count { (p) WHERE p.current_stock = 0 } AS outOfStock
                """
                prod = session.run(query_products).single()

                # ===============================================
                # WAREHOUSES
                # ===============================================
                query_warehouses = """
                MATCH (w:Warehouse)
                OPTIONAL MATCH (w)-[:CONTAINS]->(p:Product)
                WITH w, count(p) AS used
                RETURN w.id AS id, w.name AS name, 
                       used AS used, w.capacity AS capacity
                ORDER BY used DESC LIMIT 5
                """
                top_warehouses = []
                total_capacity = 0
                total_used = 0
                for record in session.run(query_warehouses):
                    capacity = record["capacity"] or 1
                    usage_rate = round((record["used"] / capacity) * 100, 2)
                    top_warehouses.append(
                        {
                            "id": record["id"],
                            "name": record["name"],
                            "usage": usage_rate,
                        }
                    )
                    total_used += record["used"]
                    total_capacity += capacity

                utilization_rate = (
                    round((total_used / total_capacity) * 100, 2)
                    if total_capacity > 0
                    else 0
                )

            # ===============================================
            # RETORNO PADRONIZADO PARA O FRONTEND
            # ===============================================
            analytics = {
                "orders": {
                    "total": total_orders,
                    "byStatus": by_status,
                    "byPeriod": by_period,
                },
                "products": {
                    "lowStock": prod["lowStock"],
                    "outOfStock": prod["outOfStock"],
                    "totalMovements": prod["totalMovements"],
                },
                "warehouses": {
                    "utilizationRate": utilization_rate,
                    "topWarehouses": top_warehouses,
                },
            }

            return Response(analytics, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Erro ao consultar o Neo4j: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
