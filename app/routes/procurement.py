from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.procurement_rule import ProcurementRule
from app.models.procurement_request import ProcurementRequest
from app.models.product import Product
from app.models.vendor import Vendor
from app.forms.bom_forms import ProcurementRuleForm
from app.utils.decorators import permission_required

procurement_bp = Blueprint(
    "procurement", __name__, template_folder="../templates/procurement"
)


@procurement_bp.route("/")
@login_required
@permission_required("run_procurement")
def dashboard():
    rules = ProcurementRule.query.all()
    requests = ProcurementRequest.query.order_by(
        ProcurementRequest.created_at.desc()
    ).limit(20).all()
    return render_template(
        "procurement/automation.html", rules=rules, requests=requests
    )


@procurement_bp.route("/rules/create", methods=["GET", "POST"])
@login_required
@permission_required("run_procurement")
def create_rule():
    form = ProcurementRuleForm()
    form.product_id.choices = [
        (p.id, f"{p.name} ({p.sku})")
        for p in Product.query.filter_by(is_active=True).order_by(Product.name).all()
    ]
    form.vendor_id.choices = [
        (v.id, v.name) for v in Vendor.query.order_by(Vendor.name).all()
    ]
    if form.validate_on_submit():
        rule = ProcurementRule(
            product_id=form.product_id.data,
            procurement_type=form.procurement_type.data,
            source_type=form.source_type.data,
            vendor_id=form.vendor_id.data,
            lead_time_days=form.lead_time_days.data,
            min_order_qty=form.min_order_qty.data,
            max_order_qty=form.max_order_qty.data,
            multiple_qty=form.multiple_qty.data,
        )
        db.session.add(rule)
        db.session.commit()
        flash("Procurement rule created.", "success")
        return redirect(url_for("procurement.dashboard"))
    return render_template("procurement/create_rule.html", form=form)


@procurement_bp.route("/run", methods=["POST"])
@login_required
@permission_required("run_procurement")
def run_procurement():
    from app.services.procurement.procurement_engine import ProcurementEngine
    engine = ProcurementEngine()
    requests_created = engine.run()
    flash(f"Procurement run complete. {requests_created} requests created.", "success")
    return redirect(url_for("procurement.dashboard"))
