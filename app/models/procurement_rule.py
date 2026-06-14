from app.extensions import db
from datetime import datetime


class ProcurementRule(db.Model):
    __tablename__ = "procurement_rules"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    procurement_type = db.Column(db.String(20), default="mts")
    source_type = db.Column(db.String(20), default="purchase")
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"))
    bom_id = db.Column(db.Integer, db.ForeignKey("boms.id"))
    lead_time_days = db.Column(db.Integer, default=0)
    min_order_qty = db.Column(db.Float, default=0.0)
    max_order_qty = db.Column(db.Float, default=0.0)
    multiple_qty = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("procurement_rules", cascade="all, delete-orphan"))
    vendor = db.relationship("Vendor", backref="procurement_rules")
    bom = db.relationship("Bom", backref="procurement_rules")

    def __repr__(self):
        return f"<ProcurementRule {self.product_id} type={self.procurement_type}>"
