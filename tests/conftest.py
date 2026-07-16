import pytest

from app import create_app
from app.extensions import cache, db, limiter
from config import TestConfig


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.drop_all()
        db.create_all()
        cache.clear()
        try:
            limiter.reset()
        except Exception:
            pass
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register_customer(client, number=1):
    return client.post(
        "/customers/",
        json={
            "name": f"Customer {number}",
            "email": f"customer{number}@example.com",
            "password": "password123",
        },
    )


def customer_token(client, number=1):
    response = client.post(
        "/customers/login",
        json={"email": f"customer{number}@example.com", "password": "password123"},
    )
    return response.get_json()["token"]


def register_mechanic(client, number=1):
    return client.post(
        "/mechanics/",
        json={
            "name": f"Mechanic {number}",
            "email": f"mechanic{number}@example.com",
            "password": "wrench123",
            "specialty": "Diagnostics",
        },
    )


def mechanic_token(client, number=1):
    response = client.post(
        "/mechanics/login",
        json={"email": f"mechanic{number}@example.com", "password": "wrench123"},
    )
    return response.get_json()["token"]


def bearer(token):
    return {"Authorization": f"Bearer {token}"}
