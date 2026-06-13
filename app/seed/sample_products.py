from app.extensions import db
from app.models.category import Category
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.bom import Bom
from app.models.bom_component import BomComponent


def seed_sample_products():
    categories_data = [
        "Raw Materials", "Components", "Finished Goods", "Packaging", "Tools"
    ]
    for cat_name in categories_data:
        if not Category.query.filter_by(name=cat_name).first():
            db.session.add(Category(name=cat_name))
    db.session.flush()
    raw_cat = Category.query.filter_by(name="Raw Materials").first()
    finished_cat = Category.query.filter_by(name="Finished Goods").first()
    products_data = [
        {"name": "Steel Sheet 2mm", "sku": "RAW-STL-001", "product_type": "raw_material", "cost_price": 3600.00, "sales_price": 5200.00, "category": raw_cat, "reorder_level": 50, "safety_stock": 20},
        {"name": "Aluminum Rod 10mm", "sku": "RAW-ALM-002", "product_type": "raw_material", "cost_price": 2400.00, "sales_price": 3840.00, "category": raw_cat, "reorder_level": 40, "safety_stock": 15},
        {"name": "Copper Wire 1mm", "sku": "RAW-CPR-003", "product_type": "raw_material", "cost_price": 6400.00, "sales_price": 9600.00, "category": raw_cat, "reorder_level": 30, "safety_stock": 10},
        {"name": "Plastic Granules ABS", "sku": "RAW-PLS-004", "product_type": "raw_material", "cost_price": 960.00, "sales_price": 1760.00, "category": raw_cat, "reorder_level": 100, "safety_stock": 30},
        {"name": "Machine Base Frame", "sku": "FG-MBF-001", "product_type": "finished_goods", "cost_price": 20000.00, "sales_price": 36000.00, "category": finished_cat, "reorder_level": 10, "safety_stock": 5},
        {"name": "Motor Assembly A1", "sku": "FG-MTR-002", "product_type": "finished_goods", "cost_price": 14400.00, "sales_price": 25600.00, "category": finished_cat, "reorder_level": 15, "safety_stock": 5},
    ]
    for pd in products_data:
        if not Product.query.filter_by(sku=pd["sku"]).first():
            product = Product(**pd)
            db.session.add(product)
            db.session.flush()
            inv = Inventory(product_id=product.id, on_hand_qty=100)
            db.session.add(inv)
    db.session.commit()
    # Create a sample BOM
    base_frame = Product.query.filter_by(sku="FG-MBF-001").first()
    steel = Product.query.filter_by(sku="RAW-STL-001").first()
    aluminum = Product.query.filter_by(sku="RAW-ALM-002").first()
    if base_frame and steel and not Bom.query.filter_by(product_id=base_frame.id).first():
        bom = Bom(product_id=base_frame.id, name="BOM for Machine Base Frame", quantity=1, is_active=True)
        db.session.add(bom)
        db.session.flush()
        db.session.add(BomComponent(bom_id=bom.id, product_id=steel.id, quantity=2, unit_cost=steel.cost_price, total_cost=steel.cost_price * 2))
        db.session.add(BomComponent(bom_id=bom.id, product_id=aluminum.id, quantity=1, unit_cost=aluminum.cost_price, total_cost=aluminum.cost_price))
        bom.calculate_cost()
    db.session.commit()
