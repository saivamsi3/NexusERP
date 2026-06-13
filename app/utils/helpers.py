from app.extensions import db
from app.models.audit_log import AuditLog


def log_audit(user_id, action, module, reference_type=None, reference_id=None, reference_number=None, description=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        module=module,
        reference_type=reference_type,
        reference_id=reference_id,
        reference_number=reference_number,
        description=description,
    )
    db.session.add(log)
    db.session.commit()
    return log


def generate_order_number(prefix, model_class):
    count = model_class.query.count()
    return f"{prefix}-{count + 1:05d}"


def format_currency(amount):
    return f"₹{amount:,.2f}" if amount else "₹0.00"
