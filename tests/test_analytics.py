def test_analytics_dashboard_and_api(client, db):
    from app.models.role import Role
    from app.models.user import User
    from app.models.category import Category
    from app.models.product import Product
    from app.models.inventory import Inventory
    from app.seed.roles_seed import seed_roles_and_permissions
    
    # Ensure test database is completely clean from any auto-seeded data
    db.drop_all()
    db.create_all()
    seed_roles_and_permissions()
    
    # Setup owner user who has permission to view reports
    role = Role.query.filter_by(name="Business Owner").first()
    user = User(username="owner_analytics_test", email="owner_test@test.com", role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)
    
    # Setup sample categories and products
    cat = Category(name="Furniture Component")
    db.session.add(cat)
    db.session.flush()
    
    # 1. Product made in-house
    p_made = Product(
        name="Made Desk",
        sku="FG-MDE-001",
        product_type="finished_goods",
        category_id=cat.id,
        cost_price=1000.0,
        sales_price=2000.0,
        is_active=True
    )
    # 2. Product bought from outside
    p_bought = Product(
        name="Bought Steel",
        sku="RAW-STL-002",
        product_type="raw_material",
        category_id=cat.id,
        cost_price=200.0,
        sales_price=300.0,
        is_active=True
    )
    db.session.add(p_made)
    db.session.add(p_bought)
    db.session.flush()
    
    # Set inventory balances
    inv_made = Inventory(product_id=p_made.id, on_hand_qty=5.0)
    inv_bought = Inventory(product_id=p_bought.id, on_hand_qty=10.0)
    db.session.add(inv_made)
    db.session.add(inv_bought)
    db.session.commit()
    
    # Log in
    client.post("/auth/login", data={"username": "owner_analytics_test", "password": "pass123"})
    
    # Verify dashboard renders
    response = client.get("/analytics/")
    assert response.status_code == 200
    assert b"Business Analytics" in response.data
    assert b"Sourcing Mix: Made vs. Bought" in response.data
    
    # Verify made vs bought API
    response = client.get("/analytics/api/made-vs-bought")
    assert response.status_code == 200
    data = response.get_json()
    assert "made" in data
    assert "bought" in data
    assert data["made"]["count"] == 1
    assert data["made"]["valuation"] == 5000.0
    assert data["bought"]["count"] == 1
    assert data["bought"]["valuation"] == 2000.0
