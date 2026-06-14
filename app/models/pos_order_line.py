from app.extensions import db


class PosOrderLine(db.Model):
    __tablename__ = "pos_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    pos_order_id = db.Column(db.Integer, db.ForeignKey("pos_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, default=0.0)
    tax_percent = db.Column(db.Float, default=0.0)
    discount_percent = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, default=0.0)

    product = db.relationship("Product", backref=db.backref("pos_order_lines", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<PosOrderLine {self.product_id} qty={self.quantity}>"
