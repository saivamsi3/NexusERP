from app.extensions import db
from datetime import datetime


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(80), unique=True, nullable=False)
    invoice_type = db.Column(db.String(20), nullable=False)  # sales, purchase
    sales_order_id = db.Column(db.Integer, db.ForeignKey("sales_orders.id"), nullable=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="draft")  # draft, open, paid, cancelled
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales_order = db.relationship("SalesOrder", backref=db.backref("invoices", lazy="dynamic"))
    purchase_order = db.relationship("PurchaseOrder", backref=db.backref("invoices", lazy="dynamic"))
    customer = db.relationship("Customer", backref=db.backref("invoices", lazy="dynamic"))
    vendor = db.relationship("Vendor", backref=db.backref("invoices", lazy="dynamic"))
    lines = db.relationship("InvoiceLine", backref="invoice", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} type={self.invoice_type} status={self.status}>"
