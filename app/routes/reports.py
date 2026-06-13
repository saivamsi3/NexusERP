from flask import Blueprint, render_template, request
from flask_login import login_required
from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.stock_ledger import StockLedger
from app.models.product import Product
from app.models.inventory import Inventory
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.utils.decorators import permission_required

reports_bp = Blueprint("reports", __name__, template_folder="../templates/reports")


@reports_bp.route("/")
@login_required
@permission_required("view_reports")
def index():
    return render_template("reports/reports.html")


@reports_bp.route("/sales")
@login_required
@permission_required("view_reports")
def sales_report():
    period = request.args.get("period", "month")
    days = {"week": 7, "month": 30, "quarter": 90, "year": 365}.get(period, 30)
    since = datetime.utcnow() - timedelta(days=days)
    sales = (
        db.session.query(
            func.date(SalesOrder.order_date).label("date"),
            func.count(SalesOrder.id).label("count"),
            func.sum(SalesOrder.total_amount).label("total"),
        )
        .filter(SalesOrder.order_date >= since)
        .group_by(func.date(SalesOrder.order_date))
        .order_by(func.date(SalesOrder.order_date))
        .all()
    )
    return render_template("reports/sales_report.html", sales=sales, period=period)


@reports_bp.route("/inventory-valuation")
@login_required
@permission_required("view_reports")
def inventory_valuation():
    items = (
        db.session.query(
            Product.name,
            Product.sku,
            Inventory.on_hand_qty,
            Product.cost_price,
            (Inventory.on_hand_qty * Product.cost_price).label("value"),
        )
        .join(Inventory, Product.id == Inventory.product_id)
        .order_by(Product.name)
        .all()
    )
    total_value = sum(item.value for item in items)
    return render_template(
        "reports/valuation.html", items=items, total_value=total_value
    )
