import os
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Ensure the app imports use the package path
os.environ["FLASK_ENV"] = "testing"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["SECRET_KEY"] = "test-secret"

@pytest.fixture(scope="session")
def app() -> Flask:
    """
    Create a Flask app configured for testing with in-memory SQLite.
    """
    from app import create_app
    from app.config import BaseConfig

    class TestConfig(BaseConfig):
        TESTING = True
        DEBUG = False
        # Use in-memory SQLite for isolation
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        # Avoid CORS affecting tests
        CORS_ORIGINS = "*"
        # Shorter token lifetime not necessary, keep defaults

    app = create_app(TestConfig)
    return app


@pytest.fixture(scope="session")
def _db(app: Flask) -> SQLAlchemy:
    """
    Provide a database for tests, creating all tables once per session.
    """
    from app.extensions import db
    with app.app_context():
        db.create_all()
        # Seed initial roles so RBAC logic has required roles
        from app.seed import seed_initial_roles
        seed_initial_roles()
    return db


@pytest.fixture(autouse=True)
def session(_db):
    """
    Run each test inside a transaction that gets rolled back.
    Ensures isolation across tests.
    """
    connection = _db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)

    _db.session = session
    try:
        yield session
    finally:
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def client(app: Flask):
    """
    Provide a Flask test client.
    """
    return app.test_client()


@pytest.fixture
def register_user(client):
    """
    Helper to register a user. Returns the created user JSON.
    Usage: user = register_user(email=..., password=..., roles=[...])
    """
    def _register(email: str, password: str, **kwargs):
        payload = {
            "email": email,
            "password": password,
        }
        payload.update(kwargs)
        res = client.post("/auth/register", json=payload)
        return res
    return _register


@pytest.fixture
def login_user(client):
    """
    Helper to login a user. Returns (access_token, refresh_token, user_json)
    """
    def _login(email: str, password: str):
        res = client.post("/auth/login", json={"email": email, "password": password})
        return res
    return _login


def auth_headers(token: str) -> dict:
    """
    Build Authorization header for a given JWT access token.
    """
    return {"Authorization": f"Bearer {token}"}
