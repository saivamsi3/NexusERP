from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.audit_log import AuditLog
from app.utils.decorators import permission_required

audit_bp = Blueprint("audit", __name__, template_folder="../templates/audit")


@audit_bp.route("/")
@login_required
@permission_required("view_audit")
def logs():
    page = request.args.get("page", 1, type=int)
    module = request.args.get("module")
    query = AuditLog.query
    if module:
        query = query.filter_by(module=module)
    logs = query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    modules = (
        AuditLog.query.with_entities(AuditLog.module).distinct().order_by(AuditLog.module).all()
    )
    return render_template("audit/logs.html", logs=logs, modules=[m[0] for m in modules])
