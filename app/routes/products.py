from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.product import Product
from app.models.category import Category
from app.forms.product_forms import ProductForm, CategoryForm
from app.utils.decorators import permission_required

products_bp = Blueprint("products", __name__, template_folder="../templates/products")


@products_bp.route("/")
@login_required
@permission_required("view_products")
def list_products():
    page = request.args.get("page", 1, type=int)
    category_id = request.args.get("category_id", type=int)
    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20
    )
    categories = Category.query.all()
    return render_template(
        "products/list.html", products=products, categories=categories
    )


@products_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("create_products")
def create_product():
    form = ProductForm()
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            sku=form.sku.data,
            barcode=form.barcode.data,
            category_id=form.category_id.data,
            description=form.description.data,
            cost_price=form.cost_price.data,
            sales_price=form.sales_price.data,
            tax_percent=form.tax_percent.data,
            product_type=form.product_type.data,
            unit_of_measure=form.unit_of_measure.data,
            reorder_level=form.reorder_level.data,
            safety_stock=form.safety_stock.data,
            procurement_type=form.procurement_type.data,
            lead_time_days=form.lead_time_days.data,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{product.name}' created.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/create.html", form=form)


@products_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("edit_products")
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    if form.validate_on_submit():
        product.name = form.name.data
        product.sku = form.sku.data
        product.barcode = form.barcode.data
        product.category_id = form.category_id.data
        product.description = form.description.data
        product.cost_price = form.cost_price.data
        product.sales_price = form.sales_price.data
        product.tax_percent = form.tax_percent.data
        product.product_type = form.product_type.data
        product.unit_of_measure = form.unit_of_measure.data
        product.reorder_level = form.reorder_level.data
        product.safety_stock = form.safety_stock.data
        product.procurement_type = form.procurement_type.data
        product.lead_time_days = form.lead_time_days.data
        db.session.commit()
        flash(f"Product '{product.name}' updated.", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/edit.html", form=form, product=product)


@products_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@permission_required("delete_products")
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash(f"Product '{product.name}' deleted.", "success")
    return redirect(url_for("products.list_products"))


@products_bp.route("/categories")
@login_required
@permission_required("view_products")
def list_categories():
    categories = Category.query.all()
    return render_template("products/categories.html", categories=categories)


@products_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
@permission_required("create_products")
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash(f"Category '{category.name}' created.", "success")
        return redirect(url_for("products.list_categories"))
    return render_template("products/create_category.html", form=form)
