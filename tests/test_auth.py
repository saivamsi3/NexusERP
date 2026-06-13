def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_register(client, db):
    from app.models.user import User
    from app.models.role import Role
    role = Role(name="Staff", description="Staff role")
    db.session.add(role)
    db.session.commit()
    response = client.post("/auth/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert User.query.filter_by(username="testuser").first() is not None


def test_forgot_password(client, db):
    from app.models.user import User
    user = User(username="recoverme", email="recover@example.com")
    user.set_password("oldpass123")
    db.session.add(user)
    db.session.commit()
    response = client.post("/auth/forgot-password", data={
        "username_or_email": "recoverme",
        "new_password": "newpass123",
        "confirm_password": "newpass123",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert user.check_password("newpass123")


def test_users_list_admin_only(client, db):
    from app.models.user import User
    from app.models.role import Role
    from app.models.permission import Permission
    
    admin_role = Role.query.filter_by(name="Admin").first()
    assert admin_role is not None
    
    admin_user = User(username="admin", email="admin@test.com", role_id=admin_role.id)
    admin_user.set_password("adminpass")
    db.session.add(admin_user)
    db.session.commit()
    
    # Try unauthorized access
    response = client.get("/auth/users")
    assert response.status_code == 302
    
    # Log in
    client.post("/auth/login", data={"username": "admin", "password": "adminpass"}, follow_redirects=True)
    response = client.get("/auth/users")
    assert response.status_code == 200
