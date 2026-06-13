from app.extensions import db
from app.models.procurement_rule import ProcurementRule
from app.models.procurement_request import ProcurementRequest
from app.models.inventory import Inventory
from app.models.product import Product
from datetime import datetime


# Procurement engine
class ProcurementEngine:
    # Run engine
    def run(self):
        from app.models.manufacturing_order import ManufacturingOrder
        from app.models.purchase_order import PurchaseOrder
        from app.models.purchase_order_line import PurchaseOrderLine
        from app.models.vendor import Vendor

        requests_created = 0
        products = Product.query.filter_by(is_active=True).all()

        for product in products:
            inv = product.inventory
            on_hand = inv.on_hand_qty if inv else 0.0
            reserved = inv.reserved_qty if inv else 0.0
            available = on_hand - reserved

            target_level = max(product.reorder_level or 0.0, 0.0)

            # Determine shortage quantity
            needed_qty = 0.0
            if available < target_level:
                needed_qty = target_level - available
            elif available <= 0.0:
                needed_qty = 1.0  # Fallback minimum if out of stock and target is 0

            if needed_qty <= 0.0:
                continue

            # Apply rule constraints if a rule exists
            rule = ProcurementRule.query.filter_by(product_id=product.id, is_active=True).first()
            if rule:
                min_qty = rule.min_order_qty or 0.0
                needed_qty = max(needed_qty, min_qty)

            # Check if there is already an open procurement request for this product
            existing_req = ProcurementRequest.query.filter_by(product_id=product.id, status="open").first()
            if existing_req:
                continue

            # Sourcing decision: Made In-House (has BOM) vs Bought from Outside (no BOM)
            is_manufacture = (product.bom is not None) or (rule and rule.source_type == "manufacture")

            if is_manufacture:
                bom_id = product.bom.id if product.bom else (rule.bom_id if rule else None)
                mo = ManufacturingOrder(
                    mo_number=self._generate_mo_number(),
                    product_id=product.id,
                    bom_id=bom_id,
                    quantity=needed_qty,
                    status="draft",
                    notes=f"Auto-created from Smart Purchasing. Shortage: {needed_qty} units",
                )
                db.session.add(mo)
                db.session.flush()

                req = ProcurementRequest(
                    request_number=self._generate_pr_number(),
                    product_id=product.id,
                    quantity=needed_qty,
                    source_type="manufacture",
                    mo_id=mo.id,
                    status="open",
                    notes=f"Auto-created from Smart Purchasing.",
                )
                db.session.add(req)
                requests_created += 1

            else:
                # Find vendor
                vendor_id = rule.vendor_id if (rule and rule.vendor_id) else None
                if not vendor_id:
                    vendor = Vendor.query.first()
                    vendor_id = vendor.id if vendor else None

                po = None
                if vendor_id:
                    po = PurchaseOrder(
                        order_number=self._generate_po_number(),
                        vendor_id=vendor_id,
                        status="draft",
                        notes=f"Auto-created from Smart Purchasing. Shortage: {needed_qty} units",
                    )
                    db.session.add(po)
                    db.session.flush()

                    line = PurchaseOrderLine(
                        purchase_order_id=po.id,
                        product_id=product.id,
                        quantity=needed_qty,
                        unit_cost=product.cost_price,
                        line_total=needed_qty * product.cost_price,
                    )
                    db.session.add(line)
                    po.subtotal = line.line_total
                    po.total_amount = line.line_total

                req = ProcurementRequest(
                    request_number=self._generate_pr_number(),
                    product_id=product.id,
                    quantity=needed_qty,
                    source_type="purchase",
                    po_id=po.id if po else None,
                    status="open",
                    notes=f"Auto-created from Smart Purchasing.",
                )
                db.session.add(req)
                requests_created += 1

        db.session.commit()
        return requests_created

    # Generate MO
    def _generate_mo_number(self):
        from app.models.manufacturing_order import ManufacturingOrder
        prefix = "MO"
        last = ManufacturingOrder.query.order_by(ManufacturingOrder.id.desc()).first()
        seq = (last.id + 1) if last else 1
        return f"{prefix}-{datetime.now().strftime('%Y%m')}-{seq:04d}"

    # Generate PO
    def _generate_po_number(self):
        from app.models.purchase_order import PurchaseOrder
        prefix = "PO"
        last = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
        seq = (last.id + 1) if last else 1
        return f"{prefix}-{datetime.now().strftime('%Y%m')}-{seq:04d}"

    # Generate PR
    def _generate_pr_number(self):
        from app.models.procurement_request import ProcurementRequest
        prefix = "PR"
        last = ProcurementRequest.query.order_by(ProcurementRequest.id.desc()).first()
        seq = (last.id + 1) if last else 1
        return f"{prefix}-{datetime.now().strftime('%Y%m')}-{seq:04d}"
