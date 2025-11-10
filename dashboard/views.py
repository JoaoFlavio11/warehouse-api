from django.http import JsonResponse
from neomodel import db
from neomodel.exceptions import DoesNotExist

# A neomodel não é um ORM Django, então não podemos usar .objects.count()
# Precisamos usar consultas Cypher diretas através do objeto 'db' da neomodel.

def dashboard_stats(request):
    # 1. Total de Warehouses (Armazéns)
    # Contar todos os nós rotulados como 'Warehouse'
    query_warehouses = "MATCH (w:Warehouse) RETURN count(w) AS total_warehouses"
    results_warehouses, _ = db.cypher_query(query_warehouses)
    total_warehouses = results_warehouses[0][0] if results_warehouses else 0

    # 2. Total de Pedidos (Orders)
    # Contar todos os nós rotulados como 'Order'
    query_orders = "MATCH (o:Order) RETURN count(o) AS total_orders"
    results_orders, _ = db.cypher_query(query_orders)
    total_orders = results_orders[0][0] if results_orders else 0

    # 3. Pedidos Pendentes (Pending Orders)
    # Contar nós 'Order' com a propriedade 'status' igual a 'pending'
    # Assumindo que o status é uma propriedade do nó Order, como no modelo Django original.
    query_pending_orders = "MATCH (o:Order {status: 'pending'}) RETURN count(o) AS pending_orders"
    results_pending_orders, _ = db.cypher_query(query_pending_orders)
    pending_orders = results_pending_orders[0][0] if results_pending_orders else 0

    # 4. Total de Produtos
    # Contar todos os nós rotulados como 'Product'
    query_products = "MATCH (p:Product) RETURN count(p) AS total_products"
    results_products, _ = db.cypher_query(query_products)
    total_products = results_products[0][0] if results_products else 0

    # 5. Estoque Crítico (Critical Stock)
    # Este é um dado mais complexo, mas podemos simular uma contagem de produtos
    # que estão em um estado de estoque crítico (ex: quantidade < 10)
    # Assumindo que o nó Product tem uma propriedade 'quantity'
    query_critical_stock = "MATCH (p:Product) WHERE p.quantity < 10 RETURN count(p) AS critical_stock"
    results_critical_stock, _ = db.cypher_query(query_critical_stock)
    critical_stock = results_critical_stock[0][0] if results_critical_stock else 0

    # 6. Ocupação Média (Average Occupancy)
    # Este é um dado de negócio que requer mais contexto (ex: capacidade total vs. ocupação atual).
    # Manteremos o mock, pois a consulta Cypher seria muito específica sem os modelos completos.
    average_occupancy = 72.5 # Mock

    data = {
        "totalWarehouses": total_warehouses,
        "totalProducts": total_products,
        "totalOrders": total_orders,
        "pendingOrders": pending_orders,
        "averageOccupancy": average_occupancy, # Manter mock
        "criticalStock": critical_stock,
    }
    return JsonResponse(data)