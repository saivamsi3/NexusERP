from app.extensions import db
from datetime import datetime


class StockLedger(db.Model):
    __tablename__ = "stock_ledger"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    movement_type = db.Column(db.String(60), nullable=False)
    reference_type = db.Column(db.String(60))
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(80))
    quantity = db.Column(db.Float, nullable=False)
    before_qty = db.Column(db.Float, default=0.0)
    after_qty = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("stock_entries", cascade="all, delete-orphan"))
    entry_user = db.relationship("User", backref="stock_entries")

    def __repr__(self):
        return f"<StockLedger {self.movement_type} qty={self.quantity}>"
