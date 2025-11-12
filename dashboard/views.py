from django.http import JsonResponse
from neomodel import db

def dashboard_stats(request):
    """
    Obtém estatísticas reais do banco Neo4j (sem mock).
    """

    try:
        # 1️⃣ Total de armazéns
        query_warehouses = "MATCH (w:Warehouse) RETURN count(w) AS total_warehouses"
        results_warehouses, _ = db.cypher_query(query_warehouses)
        total_warehouses = results_warehouses[0][0] if results_warehouses else 0

        # 2️⃣ Total de produtos
        query_products = "MATCH (p:Product) RETURN count(p) AS total_products"
        results_products, _ = db.cypher_query(query_products)
        total_products = results_products[0][0] if results_products else 0

        # 3️⃣ Total de pedidos
        query_orders = "MATCH (o:Order) RETURN count(o) AS total_orders"
        results_orders, _ = db.cypher_query(query_orders)
        total_orders = results_orders[0][0] if results_orders else 0

        # 4️⃣ Pedidos pendentes
        query_pending_orders = "MATCH (o:Order {status: 'pending'}) RETURN count(o) AS pending_orders"
        results_pending, _ = db.cypher_query(query_pending_orders)
        pending_orders = results_pending[0][0] if results_pending else 0

        # 5️⃣ Estoque crítico (produtos com quantity < 10)
        query_critical_stock = "MATCH (p:Product) WHERE p.quantity < 10 RETURN count(p) AS critical_stock"
        results_critical, _ = db.cypher_query(query_critical_stock)
        critical_stock = results_critical[0][0] if results_critical else 0

        # 6️⃣ Ocupação média: soma(occupied)/soma(capacity)
        # ⛏️ Ajuste: substituímos 'exists()' por 'IS NOT NULL'
        query_occupancy = """
            MATCH (b:Bin)
            WHERE b.capacity IS NOT NULL AND b.capacity > 0
            RETURN round((sum(b.occupied) / sum(b.capacity)) * 100, 1) AS average_occupancy
        """
        results_occupancy, _ = db.cypher_query(query_occupancy)
        average_occupancy = results_occupancy[0][0] if results_occupancy else 0.0

        # ✅ Monta resposta
        data = {
            "totalWarehouses": total_warehouses,
            "totalProducts": total_products,
            "totalOrders": total_orders,
            "pendingOrders": pending_orders,
            "averageOccupancy": average_occupancy,
            "criticalStock": critical_stock,
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse(
            {"error": f"Erro ao consultar o Neo4j: {str(e)}"},
            status=500
        )
