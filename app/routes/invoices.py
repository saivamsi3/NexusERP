from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.services.invoice.invoice_service import InvoiceService

invoices_bp = Blueprint("invoices", __name__, template_folder="../templates/invoices")


def has_invoice_write_permission(invoice_type):
    if current_user.role and current_user.role.name == "Business Owner":
        return True
    if invoice_type == "sales":
        return current_user.has_permission("create_sales")
    if invoice_type == "purchase":
        return current_user.has_permission("create_purchases")
    return False


@invoices_bp.route("/")
@login_required
def list_invoices():
    # Require either view_sales or view_purchases to see invoices list
    if not (current_user.has_permission("view_sales") or current_user.has_permission("view_purchases")):
        flash("You do not have permission to view invoices.", "danger")
        return redirect(url_for("dashboard.index"))

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    status_filter = request.args.get("status", "", type=str)
    type_filter = request.args.get("type", "", type=str)

    query = Invoice.query

    # Joins for searching
    query = query.outerjoin(Customer, Invoice.customer_id == Customer.id)\
                 .outerjoin(Vendor, Invoice.vendor_id == Vendor.id)

    if search:
        query = query.filter(
            Invoice.invoice_number.ilike(f"%{search}%") |
            Customer.name.ilike(f"%{search}%") |
            Vendor.name.ilike(f"%{search}%")
        )

    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    if type_filter:
        query = query.filter(Invoice.invoice_type == type_filter)
    else:
        # If user only has view_sales, only show sales invoices
        # If user only has view_purchases, only show purchase invoices
        if current_user.has_permission("view_sales") and not current_user.has_permission("view_purchases"):
            query = query.filter(Invoice.invoice_type == "sales")
        elif current_user.has_permission("view_purchases") and not current_user.has_permission("view_sales"):
            query = query.filter(Invoice.invoice_type == "purchase")

    invoices = query.order_by(Invoice.invoice_date.desc()).paginate(
        page=page, per_page=20
    )

    # Compute total values
    total_sales_invoiced = db.session.query(db.func.sum(Invoice.total_amount))\
        .filter(Invoice.invoice_type == "sales", Invoice.status != "cancelled").scalar() or 0.0
    total_purchases_invoiced = db.session.query(db.func.sum(Invoice.total_amount))\
        .filter(Invoice.invoice_type == "purchase", Invoice.status != "cancelled").scalar() or 0.0

    return render_template(
        "invoices/list.html",
        invoices=invoices,
        search=search,
        status_filter=status_filter,
        type_filter=type_filter,
        total_sales_invoiced=total_sales_invoiced,
        total_purchases_invoiced=total_purchases_invoiced
    )


@invoices_bp.route("/<int:id>")
@login_required
def view_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    # Authorization checks based on user permissions
    if invoice.invoice_type == "sales" and not current_user.has_permission("view_sales"):
        flash("You do not have permission to view sales invoices.", "danger")
        return redirect(url_for("invoices.list_invoices"))
    elif invoice.invoice_type == "purchase" and not current_user.has_permission("view_purchases"):
        flash("You do not have permission to view supplier bills.", "danger")
        return redirect(url_for("invoices.list_invoices"))

    return render_template("invoices/view.html", invoice=invoice)


@invoices_bp.route("/create/sales/<int:order_id>", methods=["POST"])
@login_required
def create_sales_invoice(order_id):
    if not has_invoice_write_permission("sales"):
        flash("You do not have permission to generate invoices.", "danger")
        return redirect(url_for("sales.view_order", id=order_id))

    invoice, err = InvoiceService.create_from_sales_order(order_id)
    if err:
        flash(err, "danger")
        return redirect(url_for("sales.view_order", id=order_id))

    flash(f"Invoice {invoice.invoice_number} generated successfully.", "success")
    return redirect(url_for("invoices.view_invoice", id=invoice.id))


@invoices_bp.route("/create/purchase/<int:order_id>", methods=["POST"])
@login_required
def create_purchase_invoice(order_id):
    if not has_invoice_write_permission("purchase"):
        flash("You do not have permission to generate supplier bills.", "danger")
        return redirect(url_for("purchase.view_order", id=order_id))

    invoice, err = InvoiceService.create_from_purchase_order(order_id)
    if err:
        flash(err, "danger")
        return redirect(url_for("purchase.view_order", id=order_id))

    flash(f"Supplier Bill {invoice.invoice_number} generated successfully.", "success")
    return redirect(url_for("invoices.view_invoice", id=invoice.id))


@invoices_bp.route("/<int:id>/pay", methods=["POST"])
@login_required
def pay_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    if not has_invoice_write_permission(invoice.invoice_type):
        flash("You do not have permission to register payments for this document.", "danger")
        return redirect(url_for("invoices.view_invoice", id=id))

    invoice, err = InvoiceService.mark_as_paid(id)
    if err:
        flash(err, "danger")
    else:
        flash(f"Invoice {invoice.invoice_number} registered as PAID.", "success")

    return redirect(url_for("invoices.view_invoice", id=id))


@invoices_bp.route("/<int:id>/cancel", methods=["POST"])
@login_required
def cancel_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    if not has_invoice_write_permission(invoice.invoice_type):
        flash("You do not have permission to cancel this document.", "danger")
        return redirect(url_for("invoices.view_invoice", id=id))

    invoice, err = InvoiceService.cancel_invoice(id)
    if err:
        flash(err, "danger")
    else:
        flash(f"Invoice {invoice.invoice_number} cancelled.", "warning")

    return redirect(url_for("invoices.view_invoice", id=id))
