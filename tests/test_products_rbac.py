def _create_user_with_role(db, username, email, role_name):
    from app.models.role import Role
    from app.models.user import User

    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=email, role_id=role.id)
    user.set_password("pass123")
    db.session.add(user)
    db.session.commit()
    return user


def test_product_creation_rbac_authorized(client, db):
    # Admin
    admin = _create_user_with_role(db, "rbac_admin", "admin@test.com", "Admin")
    # Business Owner
    owner = _create_user_with_role(db, "rbac_owner", "owner@test.com", "Business Owner")
    # Inventory Manager
    inv_mgr = _create_user_with_role(db, "rbac_inventory", "inventory@test.com", "Inventory Manager")

    for user in [admin, owner, inv_mgr]:
        # Log out any existing session first
        client.get("/auth/logout")
        # Log in
        client.post("/auth/login", data={"username": user.username, "password": "pass123"}, follow_redirects=True)
        # Verify access to products/create
        res = client.get("/products/create")
        assert res.status_code == 200, f"Role {user.role.name} should have access to create products"


def test_product_creation_rbac_unauthorized(client, db):
    # Sales User (unauthorized)
    sales = _create_user_with_role(db, "rbac_sales", "sales@test.com", "Sales User")
    # POS Cashier (unauthorized)
    cashier = _create_user_with_role(db, "rbac_cashier", "cashier@test.com", "POS Cashier")

    for user in [sales, cashier]:
        # Log out any existing session first
        client.get("/auth/logout")
        # Log in
        client.post("/auth/login", data={"username": user.username, "password": "pass123"}, follow_redirects=True)
        # Verify access is forbidden
        res = client.get("/products/create")
        assert res.status_code == 403, f"Role {user.role.name} should NOT have access to create products"
