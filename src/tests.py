import pytest
import httpx
import uuid

BASE_URL = "http://localhost:8500/api/v1/"  # Update if your server runs on a different address

# Shared fixtures for reuse
def get_test_user():
    return {
        "email": "testuser@example.com",
        "password": "TestPass123"
    }

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

#######################
# AUTH TESTS
#######################

def test_register_user(client):
    user = get_test_user()
    resp = client.post("/api/v1/auth/register", json=user)
    assert resp.status_code in [200, 409]  # Allow 409 for already registered

def test_login_user(client):
    user = get_test_user()
    data = {
        "username": user["email"],
        "password": user["password"]
    }
    resp = client.post("/api/v1/auth/login", data=data)
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    return tokens

#######################
# MENU TESTS
#######################

def test_create_category(client):
    data = {"name": "Test Category", "description": "Test Desc"}
    resp = client.post("/menu/categories", json=data)
    assert resp.status_code == 200
    category = resp.json()
    assert category["name"] == "Test Category"
    return category

def test_create_menu_item(client):
    category = test_create_category(client)
    data = {
        "name": "Test Dish",
        "price": 9.99,
        "category_id": category["id"],
        "image_url": "http://example.com/img.jpg"
    }
    resp = client.post("/menu/items", json=data)
    assert resp.status_code == 200
    item = resp.json()
    assert item["name"] == "Test Dish"
    return item

#######################
# TABLE TESTS
#######################

def test_create_table(client):
    data = {"table_number": "T-001", "capacity": 4}
    resp = client.post("/tables/", json=data)
    assert resp.status_code == 201
    table = resp.json()
    assert table["table_number"] == "T-001"
    return table

#######################
# ORDER TESTS
#######################

def test_create_order(client):
    item = test_create_menu_item(client)
    table = test_create_table(client)

    data = {
        "table_id": table["id"],
        "items": [{
            "menu_item_id": item["id"],
            "item_name": item["name"],
            "unit_price": item["price"],
            "quantity": 2
        }]
    }

    resp = client.post("/api/v1/orders/", json=data)
    assert resp.status_code == 201
    order = resp.json()
    assert order["table_id"] == table["id"]
    return order

#######################
# PAYMENT TESTS
#######################

def test_create_payment(client):
    order = test_create_order(client)
    data = {
        "order_id": order["id"],
        "customer_id": str(uuid.uuid4()),  # Mocked customer id
        "amount": 19.98,
        "method": "card"
    }
    resp = client.post("/payments/", json=data)
    assert resp.status_code == 201
    payment = resp.json()
    assert payment["order_id"] == order["id"]

#######################
# NEGATIVE TEST EXAMPLES
#######################

def test_invalid_order_creation(client):
    data = {
        "table_id": "invalid-uuid",
        "items": []
    }
    resp = client.post("/api/v1/orders/", json=data)
    assert resp.status_code == 422

def test_unauthorized_access():
    resp = httpx.get(f"{BASE_URL}/api/v1/auth/me")
    assert resp.status_code == 401
