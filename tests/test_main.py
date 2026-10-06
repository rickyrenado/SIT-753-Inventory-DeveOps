from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "Inventory Management API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_get_products():
    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) >= 1

def test_create_product():
    product = {
        "name": "Test Monitor",
        "category": "Electronics",
        "price": 250.00,
        "quantity": 10
    }

    response = client.post("/products", json=product)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Monitor"
    assert data["category"] == "Electronics"
    assert data["price"] == 250.00
    assert data["quantity"] == 10
    assert "id" in data


def test_get_product():
    response = client.get("/products/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1


def test_update_product():
    updated_product = {
        "name": "Updated Laptop",
        "category": "Electronics",
        "price": 1200.00,
        "quantity": 5
    }

    response = client.put("/products/1", json=updated_product)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Laptop"
    assert data["price"] == 1200.00
    assert data["quantity"] == 5


def test_delete_product():
    response = client.delete("/products/3")

    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"


def test_product_not_found():
    response = client.get("/products/9999")

    assert response.status_code == 404