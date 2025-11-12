# core/neo4j_driver.py
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "wms_password_123")

driver = GraphDatabase.driver(URI, auth=AUTH)
