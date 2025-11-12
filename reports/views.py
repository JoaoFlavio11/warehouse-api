from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from neomodel import db

@api_view(['GET'])
@permission_classes([AllowAny])  # 🔓 permite acesso sem autenticação
def generate_report(request):
    # --- 1. Leitura e fallback de parâmetros ---
    report_type = request.GET.get('type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    params_raw = request.GET.get('params')

    # Se o front enviar "params=[object Object]", evitar erro
    if params_raw and not report_type:
        try:
            # tenta decodificar se vier como JSON válido
            import json
            parsed = json.loads(params_raw)
            report_type = parsed.get('type', report_type)
            start_date = parsed.get('start_date', start_date)
            end_date = parsed.get('end_date', end_date)
        except Exception:
            # ignora caso não seja JSON válido
            pass

    if not report_type:
        return JsonResponse(
            {"error": "Parâmetro 'type' é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # --- 2. Tipos de relatórios ---
    if report_type == 'inventory':
        query = """
        MATCH (p:Product)
        RETURN p.name AS name, p.quantity AS quantity, p.price AS price
        ORDER BY p.name
        """
        results, _ = db.cypher_query(query)
        inventory_data = [{"name": r[0], "quantity": r[1], "price": r[2]} for r in results]
        return JsonResponse({
            "message": "Relatório de Inventário gerado com sucesso.",
            "report_type": report_type,
            "data": inventory_data
        }, status=status.HTTP_200_OK)

    elif report_type == 'orders':
        if not start_date or not end_date:
            return JsonResponse(
                {"error": "Parâmetros 'start_date' e 'end_date' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        query = """
        MATCH (o:Order)
        WHERE date(datetime({epochSeconds: toInteger(o.created_at)})) >= date($start_date)
          AND date(datetime({epochSeconds: toInteger(o.created_at)})) <= date($end_date)
        RETURN o.id AS id, o.status AS status, o.total AS total,
               date(datetime({epochSeconds: toInteger(o.created_at)})) AS created_at
        ORDER BY created_at
        """
        results, _ = db.cypher_query(query, {"start_date": start_date, "end_date": end_date})

        orders_data = [{
            "id": r[0],
            "status": r[1],
            "total": r[2],
            "created_at": str(r[3])
        } for r in results]

        return JsonResponse({
            "message": "Relatório de Pedidos gerado com sucesso.",
            "report_type": report_type,
            "data": orders_data
        }, status=status.HTTP_200_OK)

    elif report_type == 'movements':
        if not start_date or not end_date:
            return JsonResponse(
                {"error": "Parâmetros 'start_date' e 'end_date' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        query = """
        MATCH (p:Product)-[m:MOVED_TO]->(w:Warehouse)
        WHERE date(datetime({epochSeconds: toInteger(m.timestamp)})) >= date($start_date)
          AND date(datetime({epochSeconds: toInteger(m.timestamp)})) <= date($end_date)
        RETURN p.name AS product_name, w.name AS warehouse_name, m.quantity AS quantity,
               date(datetime({epochSeconds: toInteger(m.timestamp)})) AS move_date
        ORDER BY move_date
        """
        results, _ = db.cypher_query(query, {"start_date": start_date, "end_date": end_date})

        movements_data = [{
            "product_name": r[0],
            "warehouse_name": r[1],
            "quantity": r[2],
            "move_date": str(r[3])
        } for r in results]

        return JsonResponse({
            "message": "Relatório de Movimentações gerado com sucesso.",
            "report_type": report_type,
            "data": movements_data
        }, status=status.HTTP_200_OK)

    elif report_type == 'warehouses':
        query = """
        MATCH (w:Warehouse)
        OPTIONAL MATCH (w)<-[:STORES]-(p:Product)
        WITH w, sum(p.quantity) AS current_stock
        RETURN w.name AS name, w.capacity AS capacity, current_stock
        ORDER BY name
        """
        results, _ = db.cypher_query(query)

        warehouses_data = [{
            "name": r[0],
            "capacity": r[1],
            "current_stock": r[2] if r[2] else 0,
            "occupancy_rate": (r[2] / r[1] * 100) if r[1] and r[2] else 0
        } for r in results]

        return JsonResponse({
            "message": "Relatório de Armazéns gerado com sucesso.",
            "report_type": report_type,
            "data": warehouses_data
        }, status=status.HTTP_200_OK)

    return JsonResponse(
        {"error": f"Tipo de relatório '{report_type}' não suportado."},
        status=status.HTTP_400_BAD_REQUEST
    )
