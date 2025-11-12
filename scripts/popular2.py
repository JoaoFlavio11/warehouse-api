"""
Script para popular o Neo4j com dados adicionais (sem repetições)
Execute: python manage.py shell < scripts/popular2.py
"""
from warehouse.models import Warehouse, Zone, Aisle, Shelf, Bin, Product


def seed_data():
    print("🌱 Iniciando seed do warehouse (v2)...")

    # Criar novo warehouse com o campo obrigatório 'created_by'
    warehouse = Warehouse(
        name='Centro de distribuição RJ',
        addres="Rod. Washington Luiz, 2500 - Rio de Janeiro, RJ",
        total_capacity=20000.0,
        created_by="admin_script"
    ).save()
    print(f"✅ Warehouse criado: {warehouse.name}")

    # Criar zonas com tipos válidos
    zones = [
        ('Recebimento 2', 'receiving'),
        ('Armazenagem B', 'storage'),
        ('Separação 2', 'picking'),
        ('Expedição 2', 'shipping')
    ]

    for zone_name, zone_type in zones:
        zone = Zone(name=zone_name, zone_type=zone_type).save()
        warehouse.zones.connect(zone)
        print(f"✅ Zona criada: {zone_name}")

        # Criar corredores (apenas na zona de armazenagem)
        if zone_type == 'storage':
            for aisle_code in ['D', 'E', 'F']:
                aisle = Aisle(code=aisle_code).save()
                zone.aisles.connect(aisle)

                # Criar prateleiras
                for shelf_num in range(6, 11):  # 5 novas prateleiras
                    shelf_code = f"{shelf_num:02d}"
                    shelf = Shelf(code=shelf_code, levels=5).save()
                    aisle.shelves.connect(shelf)

                    # Criar bins (mais amplos)
                    for level in range(1, 6):  # 5 níveis
                        for position in ['A', 'B', 'C']:  # 3 posições
                            bin_code = f"{aisle_code}-{shelf_code}-{level:02d}-{position}"
                            bin_node = Bin(
                                code=bin_code,
                                capacity=150.0,
                                occupied=0.0
                            ).save()
                            shelf.bins.connect(bin_node)

    print(f"✅ Total de bins criados até agora: {len(Bin.nodes.all())}")

    # Criar novos produtos
    products = [
        ('PROD-006', 'Headset Gamer HyperX', 120, 'UN'),
        ('PROD-007', 'Cadeira Ergonômica', 40, 'UN'),
        ('PROD-008', 'HD Externo 1TB', 90, 'UN'),
        ('PROD-009', 'Suporte para Monitor', 180, 'UN'),
        ('PROD-010', 'Cabo HDMI 2.1', 300, 'UN'),
        ('PROD-011', 'SSD NVMe 1TB', 150, 'UN'),
        ('PROD-012', 'Fonte 750W Modular', 60, 'UN'),
        ('PROD-013', 'Gabinete Mid Tower RGB', 80, 'UN'),
        ('PROD-014', 'Placa de Vídeo RTX 4070', 25, 'UN'),
        ('PROD-015', 'Processador Ryzen 9 7900X', 35, 'UN'),
        ('PROD-016', 'Cooler Líquido Corsair', 70, 'UN'),
        ('PROD-017', 'Mousepad Gamer XXL', 150, 'UN'),
        ('PROD-018', 'Hub USB-C 7 em 1', 100, 'UN'),
        ('PROD-019', 'Notebook Lenovo ThinkPad', 45, 'UN'),
        ('PROD-020', 'Dock Station Universal', 80, 'UN'),
    ]

    bins = list(Bin.nodes.all())

    for i, (sku, name, qty, unit) in enumerate(products):
        product = Product(
            sku=sku,
            name=name,
            quantity=qty,
            unit=unit
        ).save()

        # Alocar produto em um bin
        if i < len(bins):
            bin_node = bins[-(i+1)]
            product.location.connect(bin_node)
            bin_node.occupied = qty
            bin_node.save()
            print(f"✅ Produto criado: {name} em {bin_node.code}")

    print("🎉 Seed (v2) completo com sucesso!")


seed_data()
