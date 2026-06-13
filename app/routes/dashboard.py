from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.inventory import Inventory
from app.models.manufacturing_order import ManufacturingOrder
from app.extensions import db
from sqlalchemy import func

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
            return redirect(url_for("auth.profile"))

    total_products = Product.query.count()
    total_sales = SalesOrder.query.count()
    total_purchases = PurchaseOrder.query.count()
    low_stock_items = Inventory.query.filter(
        Inventory.on_hand_qty <= Inventory.reserved_qty + 10
    ).count()
    pending_mos = ManufacturingOrder.query.filter(
        ManufacturingOrder.status.in_(["draft", "confirmed", "in_progress"])
    ).count()
    recent_sales = (
        SalesOrder.query.order_by(SalesOrder.created_at.desc()).limit(5).all()
    )
    recent_purchases = (
        PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(5).all()
    )
    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_sales=total_sales,
        total_purchases=total_purchases,
        low_stock_items=low_stock_items,
        pending_mos=pending_mos,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
    )
