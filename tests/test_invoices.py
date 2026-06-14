def test_sales_invoice_generation(client, db):
    from app.models.user import User
    from app.models.role import Role
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.category import Category
    from app.models.sales_order import SalesOrder
    from app.models.sales_order_line import SalesOrderLine
    from app.models.invoice import Invoice
    from app.services.inventory.inventory_service import InventoryService

    # 1. Setup user
    role = Role.query.filter_by(name="Sales User").first()
    user = User(username="sales_rep_inv", email="sales_rep_inv@test.com", role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)

    # 2. Create customer and product category
    customer = Customer(name="Invoiced Client", email="invclient@test.com")
    category = Category(name="Finished Goods")
    db.session.add(customer)
    db.session.add(category)
    db.session.commit()

    # 3. Create product with initial inventory
    product = Product(
        name="Invoice Table",
        sku="FG-TBL-INV",
        category_id=category.id,
        sales_price=2000.0,
        cost_price=1200.0,
        product_type="finished_product",
        is_active=True
    )
    db.session.add(product)
    db.session.commit()

    inv = InventoryService.get_or_create_inventory(product.id)
    inv.on_hand_qty = 10.0
    db.session.commit()

    # Log in
    client.post("/auth/login", data={"username": "sales_rep_inv", "password": "pass123"})

    # 4. Create Sales Order (draft) and Line
    order = SalesOrder(order_number="SO-INV-TEST", customer_id=customer.id, status="draft")
    db.session.add(order)
    db.session.flush()

    line = SalesOrderLine(
        sales_order_id=order.id,
        product_id=product.id,
        quantity=4.0,
        unit_price=product.sales_price,
        tax_percent=0.0,
        line_total=8000.0
    )
    db.session.add(line)
    order.subtotal = 8000.0
    order.total_amount = 8000.0
    db.session.commit()

    # 5. Confirm Order (reserves stock)
    client.post(f"/sales/{order.id}/confirm", follow_redirects=True)

    # 6. Generate Invoice
    response = client.post(f"/invoices/create/sales/{order.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Invoice" in response.data

    invoice = Invoice.query.filter_by(sales_order_id=order.id).first()
    assert invoice is not None
    assert invoice.invoice_type == "sales"
    assert invoice.status == "draft"
    assert invoice.total_amount == 8000.0
    assert invoice.lines.count() == 1

    # 7. View Invoice List and Detail
    response = client.get("/invoices/")
    assert response.status_code == 200
    assert invoice.invoice_number.encode() in response.data

    response = client.get(f"/invoices/{invoice.id}")
    assert response.status_code == 200
    assert invoice.invoice_number.encode() in response.data

    # 8. Mark as Paid
    response = client.post(f"/invoices/{invoice.id}/pay", follow_redirects=True)
    assert response.status_code == 200
    assert b"PAID" in response.data
    assert invoice.status == "paid"


def test_purchase_bill_generation(client, db):
    from app.models.user import User
    from app.models.role import Role
    from app.models.vendor import Vendor
    from app.models.product import Product
    from app.models.category import Category
    from app.models.purchase_order import PurchaseOrder
    from app.models.purchase_order_line import PurchaseOrderLine
    from app.models.invoice import Invoice

    # 1. Setup user
    role = Role.query.filter_by(name="Purchase User").first()
    user = User(username="purchase_rep_inv", email="pur_rep_inv@test.com", role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)

    # 2. Create vendor and product category
    vendor = Vendor(name="Invoice Supplier", email="invsupplier@test.com")
    category = Category(name="Raw Materials")
    db.session.add(vendor)
    db.session.add(category)
    db.session.commit()

    # 3. Create product
    product = Product(
        name="Invoice Raw Material",
        sku="RAW-INV-TBL",
        category_id=category.id,
        sales_price=0.0,
        cost_price=100.0,
        product_type="raw_material",
        is_active=True
    )
    db.session.add(product)
    db.session.commit()

    # Log in
    client.post("/auth/login", data={"username": "purchase_rep_inv", "password": "pass123"})

    # 4. Create Purchase Order (draft) and Line
    order = PurchaseOrder(order_number="PO-INV-TEST", vendor_id=vendor.id, status="draft")
    db.session.add(order)
    db.session.flush()

    line = PurchaseOrderLine(
        purchase_order_id=order.id,
        product_id=product.id,
        quantity=50.0,
        unit_cost=product.cost_price,
        line_total=5000.0
    )
    db.session.add(line)
    order.subtotal = 5000.0
    order.total_amount = 5000.0
    db.session.commit()

    # 5. Confirm Order
    client.post(f"/purchase/{order.id}/confirm", follow_redirects=True)

    # 6. Generate Bill
    response = client.post(f"/invoices/create/purchase/{order.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Supplier Bill" in response.data

    bill = Invoice.query.filter_by(purchase_order_id=order.id).first()
    assert bill is not None
    assert bill.invoice_type == "purchase"
    assert bill.status == "draft"
    assert bill.total_amount == 5000.0

    # 7. Cancel Bill
    response = client.post(f"/invoices/{bill.id}/cancel", follow_redirects=True)
    assert response.status_code == 200
    assert b"cancelled" in response.data
    assert bill.status == "cancelled"


def test_business_owner_invoice_access(client, db):
    from app.models.user import User
    from app.models.role import Role
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.category import Category
    from app.models.sales_order import SalesOrder
    from app.models.sales_order_line import SalesOrderLine
    from app.models.invoice import Invoice
    from app.services.inventory.inventory_service import InventoryService

    # 1. Setup user with "Business Owner" role
    role = Role.query.filter_by(name="Business Owner").first()
    user = User(username="owner_inv", email="owner_inv@test.com", role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)

    # 2. Create customer and product category
    customer = Customer(name="Owner Client", email="ownerclient@test.com")
    category = Category(name="Finished Goods Owner")
    db.session.add(customer)
    db.session.add(category)
    db.session.commit()

    # 3. Create product with initial inventory
    product = Product(
        name="Owner Table",
        sku="FG-TBL-OWNER",
        category_id=category.id,
        sales_price=3000.0,
        cost_price=1800.0,
        product_type="finished_product",
        is_active=True
    )
    db.session.add(product)
    db.session.commit()

    inv = InventoryService.get_or_create_inventory(product.id)
    inv.on_hand_qty = 10.0
    db.session.commit()

    # Log in
    client.post("/auth/login", data={"username": "owner_inv", "password": "pass123"})

    # 4. Create Sales Order (draft) and Line
    order = SalesOrder(order_number="SO-OWNER-TEST", customer_id=customer.id, status="draft")
    db.session.add(order)
    db.session.flush()

    line = SalesOrderLine(
        sales_order_id=order.id,
        product_id=product.id,
        quantity=2.0,
        unit_price=product.sales_price,
        tax_percent=0.0,
        line_total=6000.0
    )
    db.session.add(line)
    order.subtotal = 6000.0
    order.total_amount = 6000.0
    db.session.commit()

    # 5. Confirm Order
    client.post(f"/sales/{order.id}/confirm", follow_redirects=True)

    # 6. Generate Invoice (Business Owner should be allowed)
    response = client.post(f"/invoices/create/sales/{order.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Invoice" in response.data

    invoice = Invoice.query.filter_by(sales_order_id=order.id).first()
    assert invoice is not None
    assert invoice.status == "draft"

    # 7. Register payment
    response = client.post(f"/invoices/{invoice.id}/pay", follow_redirects=True)
    assert response.status_code == 200
    assert b"PAID" in response.data
    assert invoice.status == "paid"


def test_delete_all_data_except_users_with_invoices(db):
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.invoice import Invoice
    from app.services.admin.data_service import AdminDataService

    # 1. Create a user, a customer, and an invoice
    user = User(username="admin_test", email="admin_test@test.com")
    user.set_password("pass123")
    customer = Customer(name="Test Client", email="testclient@test.com")
    db.session.add(user)
    db.session.add(customer)
    db.session.commit()

    invoice = Invoice(
        invoice_number="INV-DEL-TEST",
        invoice_type="sales",
        customer_id=customer.id,
        status="draft",
        total_amount=100.0
    )
    db.session.add(invoice)
    db.session.commit()

    # Verify they exist
    assert User.query.filter_by(username="admin_test").count() == 1
    assert Customer.query.filter_by(email="testclient@test.com").count() == 1
    assert Invoice.query.filter_by(invoice_number="INV-DEL-TEST").count() == 1

    # 2. Run AdminDataService.delete_all_data_except_users()
    AdminDataService.delete_all_data_except_users()

    # 3. Verify user remains, but customer and invoice are deleted
    assert User.query.filter_by(username="admin_test").count() == 1
    assert Customer.query.filter_by(email="testclient@test.com").count() == 0
    assert Invoice.query.filter_by(invoice_number="INV-DEL-TEST").count() == 0

