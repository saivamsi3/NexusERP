import pytest
from app import create_app
from app.extensions import db as _db
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    return app


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        from app.seed.roles_seed import seed_roles_and_permissions
        seed_roles_and_permissions()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    return app.test_cli_runner()
