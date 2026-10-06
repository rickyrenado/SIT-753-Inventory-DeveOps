from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Inventory Management API",
    description="Simple inventory management system for SIT753 DevOps",
    version="1.0.0"
)


class Product(BaseModel):
    name: str
    category: str
    price: float
    quantity: int


products = [
    {
        "id": 1,
        "name": "Laptop",
        "category": "Electronics",
        "price": 1200.00,
        "quantity": 10
    },
    {
        "id": 2,
        "name": "Keyboard",
        "category": "Electronics",
        "price": 80.00,
        "quantity": 25
    },
    {
        "id": 3,
        "name": "Office Chair",
        "category": "Furniture",
        "price": 250.00,
        "quantity": 15
    }
]


@app.get("/")
def home():
    return {
        "application": "Inventory Management API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "UP"
    }


@app.get("/products")
def get_products():
    return {
        "products": products
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@app.post("/products")
def create_product(product: Product):
    new_id = max([p["id"] for p in products], default=0) + 1

    new_product = {
        "id": new_id,
        **product.model_dump()
    }

    products.append(new_product)

    return new_product


@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    for index, existing_product in enumerate(products):
        if existing_product["id"] == product_id:

            updated_product = {
                "id": product_id,
                **product.model_dump()
            }

            products[index] = updated_product

            return updated_product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for index, product in enumerate(products):
        if product["id"] == product_id:

            deleted_product = products.pop(index)

            return {
                "message": "Product deleted successfully",
                "product": deleted_product
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )

@app.get("/metrics")
def metrics():
    return {
        "application": "inventory-api",
        "status": "UP",
        "products_count": len(products)
    }