from app.extensions import db


class InvoiceLine(db.Model):
    __tablename__ = "invoice_lines"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    tax_percent = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, nullable=False)

    product = db.relationship("Product", backref=db.backref("invoice_lines", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<InvoiceLine {self.product_id} qty={self.quantity} total={self.line_total}>"
