from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.inventory import Inventory
from app.models.manufacturing_order import ManufacturingOrder
from app.extensions import db
from sqlalchemy import func
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    # Role-based redirection if user doesn't have report/dashboard access
    if not current_user.has_permission("view_reports"):
        if current_user.has_permission("view_pos"):
            return redirect(url_for("pos.terminal"))
        elif current_user.has_permission("view_sales"):
            return redirect(url_for("sales.list_orders"))
        elif current_user.has_permission("view_purchases"):
            return redirect(url_for("purchase.list_orders"))
        elif current_user.has_permission("view_manufacturing"):
            return redirect(url_for("manufacturing.list_mos"))
        elif current_user.has_permission("view_inventory"):
            return redirect(url_for("inventory.stock_view"))
        else:
            flash("Your account is pending role assignment. Please contact an administrator.", "warning")
            return redirect(url_for("auth.profile"))

    # Calculate detailed Factory Control Center metrics
    total_products = Product.query.count()
    total_sales = SalesOrder.query.count()
    total_purchases = PurchaseOrder.query.count()
    
    # Detailed inventory status
    total_stock_value = sum(
        (inv.on_hand_qty * inv.product.cost_price)
        for inv in Inventory.query.all()
        if inv.product
    )
    low_stock_items = Inventory.query.filter(
        Inventory.on_hand_qty <= Inventory.product.has(Product.safety_stock)
    ).count()
    
    total_on_hand = db.session.query(func.sum(Inventory.on_hand_qty)).scalar() or 0
    total_reserved = db.session.query(func.sum(Inventory.reserved_qty)).scalar() or 0
    total_free = total_on_hand - total_reserved

    # Pending queues
    pending_sales_orders = SalesOrder.query.filter(
        SalesOrder.status.in_(["draft", "confirmed"])
    ).order_by(SalesOrder.expected_date.asc()).all()

    manufacturing_orders_queue = ManufacturingOrder.query.filter(
        ManufacturingOrder.status.in_(["draft", "confirmed", "in_progress"])
    ).order_by(ManufacturingOrder.created_at.asc()).all()

    purchase_orders_queue = PurchaseOrder.query.filter(
        PurchaseOrder.status.in_(["draft", "confirmed"])
    ).order_by(PurchaseOrder.expected_date.asc()).all()

    # Delayed Orders
    now = datetime.utcnow()
    delayed_orders = []
    
    delayed_sales = SalesOrder.query.filter(
        SalesOrder.status.in_(["draft", "confirmed"]),
        SalesOrder.expected_date < now
    ).all()
    for so in delayed_sales:
        delayed_orders.append({
            "type": "Sales",
            "number": so.order_number,
            "partner": so.customer.name if so.customer else "Unknown",
            "expected_date": so.expected_date,
            "amount": so.total_amount,
            "status": so.status,
            "id": so.id,
            "view_url": "sales.view_order"
        })
        
    delayed_purchases = PurchaseOrder.query.filter(
        PurchaseOrder.status.in_(["draft", "confirmed"]),
        PurchaseOrder.expected_date < now
    ).all()
    for po in delayed_purchases:
        delayed_orders.append({
            "type": "Purchase",
            "number": po.order_number,
            "partner": po.vendor.name if po.vendor else "Unknown",
            "expected_date": po.expected_date,
            "amount": po.total_amount,
            "status": po.status,
            "id": po.id,
            "view_url": "purchase.view_order"
        })
    delayed_orders.sort(key=lambda x: x["expected_date"])

    # Material Shortages (raw materials with stock <= safety stock)
    material_shortages = (
        Inventory.query.join(Product)
        .filter(Product.product_type == "raw_material", Inventory.on_hand_qty <= Product.safety_stock)
        .all()
    )

    # Dynamic MO progress calculations
    def calculate_progress(mo):
        if mo.status == "completed":
            return 100
        wos = mo.work_orders.all()
        if not wos:
            return int((mo.produced_qty / mo.quantity * 100) if mo.quantity else 0)
        return int(sum(wo.completion_percent for wo in wos) / len(wos))
        
    mo_progress = {mo.id: calculate_progress(mo) for mo in manufacturing_orders_queue}

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_sales=total_sales,
        total_purchases=total_purchases,
        low_stock_items=low_stock_items,
        total_stock_value=total_stock_value,
        total_on_hand=total_on_hand,
        total_reserved=total_reserved,
        total_free=total_free,
        pending_sales_orders=pending_sales_orders,
        manufacturing_orders_queue=manufacturing_orders_queue,
        purchase_orders_queue=purchase_orders_queue,
        delayed_orders=delayed_orders,
        material_shortages=material_shortages,
        mo_progress=mo_progress
    )
