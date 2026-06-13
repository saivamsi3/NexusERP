from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_ledger import StockLedger
from sqlalchemy import func
from datetime import datetime, timedelta
from app.utils.decorators import permission_required

analytics_bp = Blueprint(
    "analytics", __name__, template_folder="../templates/analytics"
)


@analytics_bp.route("/")
@login_required
@permission_required("view_reports")
def dashboard():
    total_revenue = (
        db.session.query(func.sum(SalesOrder.total_amount))
        .filter(SalesOrder.status.in_(["delivered", "closed"]))
        .scalar()
        or 0
    )
    total_purchases = (
        db.session.query(func.sum(PurchaseOrder.total_amount))
        .filter(PurchaseOrder.status.in_(["received", "closed"]))
        .scalar()
        or 0
    )
    product_count = Product.query.count()
    low_stock_count = Inventory.query.filter(
        Inventory.on_hand_qty <= Inventory.reserved_qty
    ).count()
    return render_template(
        "analytics/dashboard.html",
        total_revenue=total_revenue,
        total_purchases=total_purchases,
        product_count=product_count,
        low_stock_count=low_stock_count,
    )


@analytics_bp.route("/api/sales-trend")
@login_required
@permission_required("view_reports")
def sales_trend():
    data = (
        db.session.query(
            func.date(SalesOrder.order_date).label("date"),
            func.sum(SalesOrder.total_amount).label("total"),
        )
        .filter(SalesOrder.order_date >= datetime.utcnow() - timedelta(days=30))
        .group_by(func.date(SalesOrder.order_date))
        .order_by(func.date(SalesOrder.order_date))
        .all()
    )
    return jsonify([{"date": str(d.date), "total": float(d.total)} for d in data])
