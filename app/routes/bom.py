from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.bom import Bom
from app.models.bom_component import BomComponent
from app.models.product import Product
from app.forms.bom_forms import BomForm
from app.utils.decorators import permission_required

bom_bp = Blueprint("bom", __name__, template_folder="../templates/bom")


@bom_bp.route("/")
@login_required
@permission_required("view_bom")
def list_boms():
    page = request.args.get("page", 1, type=int)
    boms = Bom.query.options(db.joinedload(Bom.product)).order_by(
        Bom.created_at.desc()
    ).paginate(page=page, per_page=20)
    return render_template("bom/bom_list.html", boms=boms)


@bom_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("create_bom")
def create_bom():
    form = BomForm()
    form.product_id.choices = [
        (p.id, f"{p.name} ({p.sku})")
        for p in Product.query.filter_by(is_active=True).order_by(Product.name).all()
    ]
    if form.validate_on_submit():
        bom = Bom(
            product_id=form.product_id.data,
            name=form.name.data,
            version=form.version.data,
            quantity=form.quantity.data,
            notes=form.notes.data,
        )
        db.session.add(bom)
        db.session.commit()
        flash(f"BOM '{bom.name}' created.", "success")
        return redirect(url_for("bom.view_bom", id=bom.id))
    return render_template("bom/create_bom.html", form=form)


@bom_bp.route("/<int:id>")
@login_required
@permission_required("view_bom")
def view_bom(id):
    bom = Bom.query.get_or_404(id)
    components = bom.components.all()
    operations = bom.operations.all()
    other_products = Product.query.filter(
        Product.id != bom.product_id, Product.is_active == True
    ).all()
    return render_template(
        "bom/view_bom.html",
        bom=bom,
        components=components,
        operations=operations,
        other_products=other_products,
    )


@bom_bp.route("/<int:id>/add-component", methods=["POST"])
@login_required
@permission_required("create_bom")
def add_component(id):
    bom = Bom.query.get_or_404(id)
    product_id = request.form.get("product_id", type=int)
    quantity = request.form.get("quantity", 1, type=float)
    product = Product.query.get_or_404(product_id)
    component = BomComponent(
        bom_id=bom.id,
        product_id=product_id,
        quantity=quantity,
        unit_cost=product.cost_price,
        total_cost=product.cost_price * quantity,
    )
    db.session.add(component)
    bom.calculate_cost()
    db.session.commit()
    flash("Component added.", "success")
    return redirect(url_for("bom.view_bom", id=bom.id))
