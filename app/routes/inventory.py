from flask import Blueprint, render_template, request
from flask_login import login_required
from app.extensions import db
from app.models.inventory import Inventory
from app.models.stock_ledger import StockLedger
from app.models.product import Product
from app.utils.decorators import permission_required

inventory_bp = Blueprint("inventory", __name__, template_folder="../templates/inventory")


@inventory_bp.route("/")
@login_required
@permission_required("view_inventory")
def stock_view():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    query = Inventory.query.join(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    inventory = query.order_by(Product.name).paginate(page=page, per_page=20)
    return render_template("inventory/stock.html", inventory=inventory, search=search)


@inventory_bp.route("/ledger")
@login_required
@permission_required("view_inventory")
def ledger_view():
    page = request.args.get("page", 1, type=int)
    product_id = request.args.get("product_id", type=int)
    query = StockLedger.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    entries = query.order_by(StockLedger.created_at.desc()).paginate(
        page=page, per_page=50
    )
    products = Product.query.order_by(Product.name).all()
    return render_template(
        "inventory/ledger.html", entries=entries, products=products
    )


@inventory_bp.route("/low-stock")
@login_required
@permission_required("view_inventory")
def low_stock():
    low_items = (
        db.session.query(Inventory)
        .join(Product)
        .filter(Inventory.on_hand_qty <= Product.safety_stock)
        .all()
    )
    return render_template("inventory/low_stock.html", items=low_items)
