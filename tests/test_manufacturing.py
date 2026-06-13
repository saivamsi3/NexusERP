def test_manufacturing_page(client, db):
    from app.models.user import User
    from app.models.role import Role
    role = Role.query.filter_by(name="Manufacturing User").first()
    user = User(username="mf_test", email="mf@test.com", role_id=role.id)
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    client.post("/auth/login", data={"username": "mf_test", "password": "test"})
    response = client.get("/manufacturing/")
    assert response.status_code == 200
