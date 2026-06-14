from app.extensions import db


class BomComponent(db.Model):
    __tablename__ = "bom_components"

    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey("boms.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0)
    scrap_percent = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    component_product = db.relationship("Product", backref=db.backref("bom_components", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<BomComponent {self.product_id} qty={self.quantity}>"
