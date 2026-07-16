from app import create_app
from app.extensions import db, limiter
from config import TestConfig
from tests.conftest import (
    bearer,
    customer_token,
    mechanic_token,
    register_customer,
    register_mechanic,
)


def test_customer_login_and_my_tickets(client):
    assert register_customer(client).status_code == 201
    token = customer_token(client)

    created = client.post(
        "/service-tickets/",
        json={"description": "Oil change", "status": "open"},
        headers=bearer(token),
    )
    assert created.status_code == 201

    response = client.get("/customers/my-tickets", headers=bearer(token))
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0]["description"] == "Oil change"


def test_customer_pagination(client):
    for number in range(1, 8):
        assert register_customer(client, number).status_code == 201

    response = client.get("/customers/?page=2&per_page=3")
    data = response.get_json()
    assert response.status_code == 200
    assert data["page"] == 2
    assert data["per_page"] == 3
    assert data["total"] == 7
    assert len(data["items"]) == 3


def test_inventory_crud_requires_mechanic_token(client):
    unauthorized = client.post("/inventory/", json={"name": "Air Filter", "price": 19.99})
    assert unauthorized.status_code == 401

    assert register_mechanic(client).status_code == 201
    token = mechanic_token(client)
    created = client.post(
        "/inventory/",
        json={"name": "Air Filter", "price": 19.99},
        headers=bearer(token),
    )
    assert created.status_code == 201
    item_id = created.get_json()["id"]

    updated = client.put(
        f"/inventory/{item_id}",
        json={"price": 24.99},
        headers=bearer(token),
    )
    assert updated.status_code == 200
    assert updated.get_json()["price"] == 24.99

    deleted = client.delete(f"/inventory/{item_id}", headers=bearer(token))
    assert deleted.status_code == 200


def test_edit_ticket_mechanics_and_ranked_query(client):
    register_customer(client)
    customer_jwt = customer_token(client)
    ticket = client.post(
        "/service-tickets/",
        json={"description": "Engine diagnostic"},
        headers=bearer(customer_jwt),
    ).get_json()

    register_mechanic(client, 1)
    register_mechanic(client, 2)
    mechanic_jwt = mechanic_token(client, 1)

    edited = client.put(
        f"/service-tickets/{ticket['id']}/edit",
        json={"add_ids": [1, 2], "remove_ids": []},
        headers=bearer(mechanic_jwt),
    )
    assert edited.status_code == 200
    assert len(edited.get_json()["mechanics"]) == 2

    ranked = client.get("/mechanics/ranked")
    assert ranked.status_code == 200
    assert ranked.get_json()[0]["ticket_count"] == 1
    assert ranked.get_json()[1]["ticket_count"] == 1


def test_add_inventory_part_to_ticket(client):
    register_customer(client)
    customer_jwt = customer_token(client)
    ticket_id = client.post(
        "/service-tickets/",
        json={"description": "Brake repair"},
        headers=bearer(customer_jwt),
    ).get_json()["id"]

    register_mechanic(client)
    mechanic_jwt = mechanic_token(client)
    part_id = client.post(
        "/inventory/",
        json={"name": "Brake Pad Set", "price": 79.99},
        headers=bearer(mechanic_jwt),
    ).get_json()["id"]

    response = client.put(
        f"/service-tickets/{ticket_id}/add-part/{part_id}",
        headers=bearer(mechanic_jwt),
    )
    assert response.status_code == 200
    assert response.get_json()["inventory_parts"][0]["name"] == "Brake Pad Set"


def test_login_route_rate_limit():
    class RateLimitTestConfig(TestConfig):
        RATELIMIT_ENABLED = True

    application = create_app(RateLimitTestConfig)
    with application.app_context():
        db.drop_all()
        db.create_all()
        limiter.reset()
        client = application.test_client()
        responses = [
            client.post(
                "/customers/login",
                json={"email": "missing@example.com", "password": "password123"},
            )
            for _ in range(6)
        ]
        assert responses[-1].status_code == 429
