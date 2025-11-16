#!/usr/bin/env python3
import requests
import json # Importar para formatação de saída

# Base da URL da sua API de pedidos
API_BASE = "http://localhost:8000/api/orders/"

sample_orders = [
    {
        "order_number": "SEED-001",
        "customer_name": "Cliente A",
        "items": [
            # Usando SKUs criados no seed do armazém
            {"product_sku": "PROD-001", "quantity": 2}, # Notebook Dell
            {"product_sku": "PROD-002", "quantity": 1}  # Mouse Logitech
        ]
    },
    {
        "order_number": "SEED-002",
        "customer_name": "Cliente B",
        "items": [
            # Usando SKUs criados no seed do armazém
            {"product_sku": "PROD-003", "quantity": 5}  # Teclado Mecânico
        ]
    }
]

def create_order(order_data):
    """Envia um POST request para criar um novo pedido."""
    print(f"📦 Enviando pedido: {order_data['order_number']}")
    try:
        r = requests.post(API_BASE, json=order_data)
        
        # Imprime o código de status e a resposta formatada
        print(f"   Status Code: {r.status_code}")
        try:
            # Tenta imprimir a resposta JSON formatada, se houver
            response_json = r.json()
            print("   Resposta (JSON):")
            print(json.dumps(response_json, indent=4))
        except requests.exceptions.JSONDecodeError:
            # Se não for JSON, imprime como texto
            print(f"   Resposta (Texto): {r.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ ERRO DE CONEXÃO: Não foi possível conectar a {API_BASE}. Verifique se o servidor está rodando.")
        print(f"   Detalhe: {e}")
    except Exception as e:
        print(f"   ❌ Ocorreu um erro: {e}")
    print("-" * 30)

if __name__ == "__main__":
    print("🚀 Iniciando seed de pedidos...")
    print(f"API Base: {API_BASE}")
    print("-" * 30)
    for order in sample_orders:
        create_order(order)
    print("🎉 Seed de pedidos concluído!")