from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.neo4j_driver import get_driver  # ✅ pega o driver seguro


class AnalyticsView(APIView):
    def get(self, request):
        analytics = {}

        try:
            driver = get_driver()  # ✅ sempre garante uma conexão ativa

            with driver.session() as session:
                # --- ORDERS ---
                orders_total = session.run("MATCH (o:Order) RETURN count(o) AS total").single()["total"]

                orders_by_status_result = session.run("""
                    MATCH (o:Order)
                    RETURN o.status AS status, count(o) AS count
                """)
                orders_by_status = {record["status"]: record["count"] for record in orders_by_status_result}

                orders_by_period_result = session.run("""
                    MATCH (o:Order)
                    WITH date(o.date) AS date, count(o) AS count
                    RETURN date, count ORDER BY date
                """)
                orders_by_period = [
                    {"date": str(record["date"]), "count": record["count"]}
                    for record in orders_by_period_result
                ]

                # --- PRODUCTS ---
                products_low_stock = session.run("""
                    MATCH (p:Product)
                    WHERE p.stock < 10 AND p.stock > 0
                    RETURN count(p) AS low_stock
                """).single()["low_stock"]

                products_out_of_stock = session.run("""
                    MATCH (p:Product)
                    WHERE p.stock = 0
                    RETURN count(p) AS out_of_stock
                """).single()["out_of_stock"]

                products_total_movements = session.run("""
                    MATCH (:Movement)
                    RETURN count(*) AS total_movements
                """).single()["total_movements"]

                # --- WAREHOUSES ---
                warehouses_result = session.run("""
                    MATCH (w:Warehouse)
                    RETURN w.id AS id, w.name AS name, w.utilizationRate AS usage
                    ORDER BY w.utilizationRate DESC
                    LIMIT 5
                """)
                top_warehouses = [
                    {"id": record["id"], "name": record["name"], "usage": record["usage"]}
                    for record in warehouses_result
                ]

                utilization_rate = session.run("""
                    MATCH (w:Warehouse)
                    RETURN avg(w.utilizationRate) AS utilization_rate
                """).single()["utilization_rate"]

                # --- Consolidação final ---
                analytics = {
                    "orders": {
                        "total": orders_total,
                        "byStatus": orders_by_status,
                        "byPeriod": orders_by_period,
                    },
                    "products": {
                        "lowStock": products_low_stock,
                        "outOfStock": products_out_of_stock,
                        "totalMovements": products_total_movements,
                    },
                    "warehouses": {
                        "utilizationRate": utilization_rate,
                        "topWarehouses": top_warehouses,
                    },
                }

                print("✅ Analytics gerados com sucesso")

        except Exception as e:
            print("❌ Erro ao gerar analytics:", str(e))
            return Response(
                {"error": f"Erro ao gerar analytics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(analytics, status=status.HTTP_200_OK)
