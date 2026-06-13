from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.work_order import WorkOrder
from app.models.work_center import WorkCenter
from app.models.manufacturing_order import ManufacturingOrder
from app.utils.decorators import permission_required

workorders_bp = Blueprint(
    "workorders", __name__, template_folder="../templates/manufacturing"
)


@workorders_bp.route("/")
@login_required
@permission_required("view_manufacturing")
def list_workorders():
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status")
    query = WorkOrder.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    workorders = query.order_by(WorkOrder.created_at.desc()).paginate(
        page=page, per_page=20
    )
    return render_template("manufacturing/workorders.html", workorders=workorders)


@workorders_bp.route("/<int:id>/update", methods=["POST"])
@login_required
@permission_required("create_manufacturing")
def update_status(id):
    wo = WorkOrder.query.get_or_404(id)
    wo.status = request.form.get("status", wo.status)
    wo.completion_percent = request.form.get("completion_percent", 0, type=float)
    db.session.commit()
    flash("Work order updated.", "success")
    return redirect(url_for("workorders.list_workorders"))
