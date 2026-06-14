from app.models.user import User
from app.models.role import Role

def test_admin_sees_admin_portal(client, db):
    role = Role.query.filter_by(name="Admin").first()
    user = User(username="admin_test", email="admin_test@test.com", role_id=role.id)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={"username": "admin_test", "password": "password123"}, follow_redirects=True)
    response = client.get("/dashboard/portals")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Admin Dashboard" in html
    # Since admin gets all permissions (via User.has_permission fallback), admin should see other dashboards too.
    assert "Sales Dashboard" in html
    assert "Purchase Dashboard" in html
    assert "Inventory Dashboard" in html
    assert "Manufacturing Dashboard" in html
    assert "Cashier Portal" in html
    assert "Analytics Portal" in html
    assert "No Portals Available" not in html

def test_sales_user_sees_only_sales_portal(client, db):
    role = Role.query.filter_by(name="Sales User").first()
    user = User(username="sales_test", email="sales_test@test.com", role_id=role.id)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={"username": "sales_test", "password": "password123"}, follow_redirects=True)
    response = client.get("/dashboard/portals")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    
    assert "Sales Dashboard" in html
    assert "Admin Dashboard" not in html
    assert "Purchase Dashboard" not in html
    assert "Manufacturing Dashboard" not in html
    assert "Cashier Portal" not in html
    assert "Analytics Portal" not in html
    assert "No Portals Available" not in html

def test_pos_cashier_sees_only_cashier_portal(client, db):
    role = Role.query.filter_by(name="POS Cashier").first()
    user = User(username="pos_test", email="pos_test@test.com", role_id=role.id)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={"username": "pos_test", "password": "password123"}, follow_redirects=True)
    response = client.get("/dashboard/portals")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    
    assert "Cashier Portal" in html
    assert "Admin Dashboard" not in html
    assert "Sales Dashboard" not in html
    assert "Purchase Dashboard" not in html
    assert "Inventory Dashboard" not in html
    assert "Manufacturing Dashboard" not in html
    assert "Analytics Portal" not in html
    assert "No Portals Available" not in html

def test_user_without_permissions_sees_no_portals_fallback(client, db):
    # Create a custom role with no permissions
    role = Role(name="Inactive User", description="No permissions")
    db.session.add(role)
    db.session.commit()

    user = User(username="no_perm_test", email="noperm@test.com", role_id=role.id)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    client.post("/auth/login", data={"username": "no_perm_test", "password": "password123"}, follow_redirects=True)
    response = client.get("/dashboard/portals")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    
    assert "No Portals Available" in html
    assert "Admin Dashboard" not in html
    assert "Sales Dashboard" not in html
    assert "Purchase Dashboard" not in html
    assert "Inventory Dashboard" not in html
    assert "Manufacturing Dashboard" not in html
    assert "Cashier Portal" not in html
    assert "Analytics Portal" not in html
