from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.sales_order import SalesOrder
from app.models.sales_order_line import SalesOrderLine
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.forms.sales_forms import SalesOrderForm, SalesOrderLineForm
from app.services.sales.sales_service import SalesService
from app.services.inventory.stock_service import StockService
from app.utils.decorators import permission_required

sales_bp = Blueprint("sales", __name__, template_folder="../templates/sales")


@sales_bp.route("/")
@login_required
@permission_required("view_sales")
def list_orders():
    page = request.args.get("page", 1, type=int)
    orders = SalesOrder.query.order_by(SalesOrder.created_at.desc()).paginate(
        page=page, per_page=20
    )
    return render_template("sales/orders.html", orders=orders)


@sales_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("create_sales")
def create_order():
    form = SalesOrderForm()
    form.customer_id.choices = [
        (c.id, f"{c.name} ({c.city or 'N/A'})")
        for c in Customer.query.order_by(Customer.name).all()
    ]
    if form.validate_on_submit():
        sales_service = SalesService()
        order = sales_service.create_order(
            customer_id=form.customer_id.data,
            user_id=current_user.id,
            expected_date=form.expected_date.data,
            notes=form.notes.data,
        )
        flash(f"Sales Order {order.order_number} created.", "success")
        return redirect(url_for("sales.edit_order", id=order.id))
    return render_template("sales/create_order.html", form=form)


@sales_bp.route("/<int:id>")
@login_required
@permission_required("view_sales")
def view_order(id):
    order = SalesOrder.query.get_or_404(id)
    return render_template("sales/view_order.html", order=order)


@sales_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("create_sales")
def edit_order(id):
    order = SalesOrder.query.get_or_404(id)
    form = SalesOrderForm(obj=order)
    form.customer_id.choices = [
        (c.id, f"{c.name} ({c.city or 'N/A'})")
        for c in Customer.query.order_by(Customer.name).all()
    ]
    if form.validate_on_submit():
        order.customer_id = form.customer_id.data
        order.expected_date = form.expected_date.data
        order.notes = form.notes.data
        db.session.commit()
        flash("Order updated.", "success")
        return redirect(url_for("sales.view_order", id=order.id))
    products = Product.query.filter_by(is_active=True).all()
    return render_template("sales/edit_order.html", form=form, order=order, products=products)


@sales_bp.route("/<int:id>/add-line", methods=["POST"])
@login_required
@permission_required("create_sales")
def add_line(id):
    order = SalesOrder.query.get_or_404(id)
    product_id = request.form.get("product_id", type=int)
    quantity = request.form.get("quantity", 1, type=float)
    product = Product.query.get_or_404(product_id)
    line = SalesOrderLine(
        sales_order_id=order.id,
        product_id=product_id,
        quantity=quantity,
        unit_price=product.sales_price,
        tax_percent=product.tax_percent,
        line_total=quantity * product.sales_price,
    )
    db.session.add(line)
    order.subtotal = sum(l.line_total for l in order.lines)
    order.tax_amount = sum(l.line_total * l.tax_percent / 100 for l in order.lines)
    order.total_amount = order.subtotal + order.tax_amount - order.discount_amount
    db.session.commit()
    flash("Line added.", "success")
    return redirect(url_for("sales.edit_order", id=order.id))


@sales_bp.route("/<int:id>/confirm", methods=["POST"])
@login_required
@permission_required("confirm_sales")
def confirm_order(id):
    sales_service = SalesService()
    order = sales_service.confirm_order(id)
    flash(f"Order {order.order_number} confirmed.", "success")
    return redirect(url_for("sales.view_order", id=order.id))


@sales_bp.route("/<int:id>/deliver", methods=["POST"])
@login_required
@permission_required("deliver_sales")
def deliver_order(id):
    from app.services.sales.delivery_service import DeliveryService
    delivery_service = DeliveryService()
    order = delivery_service.deliver_order(id)
    flash(f"Order {order.order_number} delivered.", "success")
    return redirect(url_for("sales.view_order", id=order.id))
