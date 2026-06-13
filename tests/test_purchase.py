def test_purchase_page(client, db):
    from app.models.user import User
    from app.models.role import Role
    role = Role.query.filter_by(name="Purchase User").first()
    user = User(username="po_test", email="po@test.com", role_id=role.id)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "po_test", "password": "test"})
    response = client.get("/purchase/")
    assert response.status_code == 200
