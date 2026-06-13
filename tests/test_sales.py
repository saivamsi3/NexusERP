def test_sales_page(client, db):
    from app.models.user import User
    from app.models.role import Role
    role = Role.query.filter_by(name="Sales User").first()
    user = User(username="sales_test", email="sales@test.com", role_id=role.id)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "sales_test", "password": "test"})
    response = client.get("/sales/")
    assert response.status_code == 200
