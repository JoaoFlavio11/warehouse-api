# core/neo4j_driver.py
from neo4j import GraphDatabase

# Configurações fixas — ajuste conforme seu ambiente
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "wms_password_123")

# Cria uma única instância global do driver (reutilizável)
driver = GraphDatabase.driver(URI, auth=AUTH, max_connection_lifetime=1000)

def get_driver():
    """Retorna uma instância válida do driver (garantido ativo)."""
    global driver
    if driver is None or driver.closed():
        driver = GraphDatabase.driver(URI, auth=AUTH, max_connection_lifetime=1000)
    return driver
