from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.product import Product
from app.models.inventory import Inventory
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
    # Consistent low stock logic: on_hand_qty <= Product.safety_stock
    low_stock_count = (
        Inventory.query.join(Product)
        .filter(Inventory.on_hand_qty <= Product.safety_stock)
        .count()
    )
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


@analytics_bp.route("/api/sales-vs-purchases")
@login_required
@permission_required("view_reports")
def sales_vs_purchases():
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=29)

    # Fetch Sales
    sales_data = (
        db.session.query(
            func.date(SalesOrder.order_date).label("date"),
            func.sum(SalesOrder.total_amount).label("total")
        )
        .filter(SalesOrder.order_date >= datetime.combine(start_date, datetime.min.time()))
        .group_by(func.date(SalesOrder.order_date))
        .all()
    )

    # Fetch Purchases
    purchases_data = (
        db.session.query(
            func.date(PurchaseOrder.order_date).label("date"),
            func.sum(PurchaseOrder.total_amount).label("total")
        )
        .filter(PurchaseOrder.order_date >= datetime.combine(start_date, datetime.min.time()))
        .group_by(func.date(PurchaseOrder.order_date))
        .all()
    )

    sales_map = {str(d.date): float(d.total or 0) for d in sales_data}
    purchases_map = {str(d.date): float(d.total or 0) for d in purchases_data}

    result = []
    curr = start_date
    while curr <= end_date:
        date_str = str(curr)
        result.append({
            "date": date_str,
            "sales": sales_map.get(date_str, 0.0),
            "purchases": purchases_map.get(date_str, 0.0)
        })
        curr += timedelta(days=1)

    return jsonify(result)


@analytics_bp.route("/api/inventory-valuation")
@login_required
@permission_required("view_reports")
def inventory_valuation():
    from app.models.category import Category
    data = (
        db.session.query(
            Category.name.label("category_name"),
            func.sum(Inventory.on_hand_qty * Product.cost_price).label("valuation")
        )
        .join(Product, Product.category_id == Category.id)
        .join(Inventory, Inventory.product_id == Product.id)
        .group_by(Category.name)
        .all()
    )
    return jsonify([
        {"category": d.category_name, "valuation": float(d.valuation or 0)}
        for d in data
    ])


@analytics_bp.route("/api/top-selling-products")
@login_required
@permission_required("view_reports")
def top_selling_products():
    from app.models.sales_order_line import SalesOrderLine
    data = (
        db.session.query(
            Product.name.label("product_name"),
            func.sum(SalesOrderLine.quantity).label("total_qty")
        )
        .join(SalesOrderLine, SalesOrderLine.product_id == Product.id)
        .group_by(Product.name)
        .order_by(db.desc("total_qty"))
        .limit(5)
        .all()
    )
    return jsonify([
        {"product": d.product_name, "quantity": float(d.total_qty or 0)}
        for d in data
    ])

