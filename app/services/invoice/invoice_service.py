from app.extensions import db
from app.models.invoice import Invoice
from app.models.invoice_line import InvoiceLine
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from datetime import datetime


class InvoiceService:
    @staticmethod
    def create_from_sales_order(sales_order_id):
        order = SalesOrder.query.get(sales_order_id)
        if not order:
            return None, "Sales Order not found"

        # Check if active invoice already exists
        existing = Invoice.query.filter_by(sales_order_id=sales_order_id, invoice_type="sales")\
            .filter(Invoice.status != "cancelled").first()
        if existing:
            return existing, None

        invoice = Invoice(
            invoice_number=InvoiceService._generate_invoice_number("INV"),
            invoice_type="sales",
            sales_order_id=order.id,
            customer_id=order.customer_id,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            status="draft",
            notes=order.notes
        )
        db.session.add(invoice)
        db.session.flush()

        for line in order.lines.all():
            inv_line = InvoiceLine(
                invoice_id=invoice.id,
                product_id=line.product_id,
                quantity=line.quantity,
                unit_price=line.unit_price,
                tax_percent=line.tax_percent,
                line_total=line.line_total
            )
            db.session.add(inv_line)

        db.session.commit()
        return invoice, None

    @staticmethod
    def create_from_purchase_order(purchase_order_id):
        order = PurchaseOrder.query.get(purchase_order_id)
        if not order:
            return None, "Purchase Order not found"

        # Check if active bill already exists
        existing = Invoice.query.filter_by(purchase_order_id=purchase_order_id, invoice_type="purchase")\
            .filter(Invoice.status != "cancelled").first()
        if existing:
            return existing, None

        invoice = Invoice(
            invoice_number=InvoiceService._generate_invoice_number("BILL"),
            invoice_type="purchase",
            purchase_order_id=order.id,
            vendor_id=order.vendor_id,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            total_amount=order.total_amount,
            status="draft",
            notes=order.notes
        )
        db.session.add(invoice)
        db.session.flush()

        for line in order.lines.all():
            inv_line = InvoiceLine(
                invoice_id=invoice.id,
                product_id=line.product_id,
                quantity=line.quantity,
                unit_price=line.unit_cost,
                tax_percent=line.tax_percent,
                line_total=line.line_total
            )
            db.session.add(inv_line)

        db.session.commit()
        return invoice, None

    @staticmethod
    def mark_as_paid(invoice_id):
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return None, "Invoice not found"
        if invoice.status == "paid":
            return invoice, None
        if invoice.status == "cancelled":
            return None, "Cancelled invoice cannot be paid"
        
        invoice.status = "paid"
        db.session.commit()
        return invoice, None

    @staticmethod
    def cancel_invoice(invoice_id):
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return None, "Invoice not found"
        if invoice.status == "paid":
            return None, "Paid invoice cannot be cancelled"
        
        invoice.status = "cancelled"
        db.session.commit()
        return invoice, None

    @staticmethod
    def _generate_invoice_number(prefix):
        last = Invoice.query.filter(Invoice.invoice_number.like(f"{prefix}-%"))\
            .order_by(Invoice.id.desc()).first()
        seq = (last.id + 1) if last else 1
        return f"{prefix}-{datetime.now().strftime('%Y%m')}-{seq:04d}"
