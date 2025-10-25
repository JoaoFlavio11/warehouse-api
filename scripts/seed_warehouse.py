"""
Script para popular o Neo4j com dados de teste
Execute: python manage.py shell < scripts/seed_warehouse.py
"""
from warehouse.models import Warehouse, Zone, Aisle, Shelf, Bin, Product

def seed_data():
    print("🌱 Iniciando seed do warehouse...")

    # criar warehouse
    warehouse = Warehouse(
        name='Centro de distribuição SP',
        addres="Av. Industrial, 1000 - São Paulo, SP",
        total_capacity=10000.0
    ).save()
    print(f"✅ Warehouse criado: {warehouse.name}")

    # criar zonas
    zones = [
        ('Recebimento', 'receiving'),
        ('Armazenagem A', 'storage'),
        ('Separação', 'picking'),
        ('Expedição', 'shipping')
    ]

    for zone_name, zone_type in zones:
        zone = Zone(name=zone_name, zone_type=zone_type).save()
        warehouse.zones.connect(zone)
        print(f"✅ Zona criada: {zone_name}")

        # Criar corredores (apenas na zona de armazenagem)
        if zone_type == 'storage':
            for aisle_code in ['A', 'B', 'C']:
                aisle = Aisle(code=aisle_code).save()
                zone.aisles.connect(aisle)

                # Criar prateleiras
                for shelf_num in range(1, 6):  # 5 prateleiras
                    shelf_code = f"{shelf_num:02d}"
                    shelf = Shelf(code=shelf_code, levels=4).save()
                    aisle.shelves.connect(shelf)

                    # Criar bins
                    for level in range(1, 5):  # 4 níveis
                        for position in ['A', 'B']:  # 2 posições por nível
                            bin_code = f"{aisle_code}-{shelf_code}-{level:02d}-{position}"
                            bin_node = Bin(
                                code=bin_code,
                                capacity=100.0,
                                occupied=0.0
                            ).save()
                            shelf.bins.connect(bin_node)

    print(f"✅ Total de bins criados: {len(Bin.nodes.all())}")

    # Criar produtos
    products = [
        ('PROD-001', 'Notebook Dell', 50, 'UN'),
        ('PROD-002', 'Mouse Logitech', 200, 'UN'),
        ('PROD-003', 'Teclado Mecânico', 100, 'UN'),
        ('PROD-004', 'Monitor 24"', 75, 'UN'),
        ('PROD-005', 'Webcam HD', 150, 'UN'),
    ]

    bins = list(Bin.nodes.all())

    for i, (sku, name, qty, unit) in enumerate(products):
        product = Product(
            sku=sku,
            name=name,
            quantity=qty,
            unit=unit
        ).save()

        # Alocar em um bin
        if i < len(bins):
            bin_node = bins[i]
            product.location.connect(bin_node)
            bin_node.occupied = qty
            bin_node.save()
            print(f"✅ Produto criado: {name} em {bin_node.code}")

    print("🎉 Seed completo!")

    if __name__ == "__main__":
        seed_data()