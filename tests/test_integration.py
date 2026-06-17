import pytest
from httpx import AsyncClient
from models.user import User
from models.product import Product
from core.security import hash_password

# Pytest marker to run all tests in this file with anyio (async)
pytestmark = pytest.mark.anyio

async def test_auth_flow(client: AsyncClient):
    # 1. Sign up a new user
    signup_payload = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "Password123",
        "gender": "male",
        "pincode": "123456"
    }
    
    response = await client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["role"] == "user"
    
    # Try signing up with the same email (should fail 400)
    response = await client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 400
    
    # 2. Login with correct credentials
    login_payload = {
        "email": "testuser@example.com",
        "password": "Password123"
    }
    response = await client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "testuser@example.com"

    # Login with wrong password (should fail 401)
    bad_login_payload = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }
    response = await client.post("/auth/login", json=bad_login_payload)
    assert response.status_code == 401

    # Login with unregistered email (should fail 404)
    non_existent_payload = {
        "email": "nonexistent@example.com",
        "password": "Password123"
    }
    response = await client.post("/auth/login", json=non_existent_payload)
    assert response.status_code == 404

async def test_users_endpoints(client: AsyncClient, db_session):
    # 1. Seed an admin user and a regular user directly in the database
    admin_user = User(
        name="Admin User",
        email="admin@example.com",
        role="admin",
        hashed_password=hash_password("AdminPass123")
    )
    regular_user = User(
        name="Regular User",
        email="user@example.com",
        role="user",
        hashed_password=hash_password("UserPass123")
    )
    db_session.add(admin_user)
    db_session.add(regular_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    await db_session.refresh(regular_user)
    
    # 2. Login as admin and regular user to get tokens
    admin_login_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123"})
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    user_login_res = await client.post("/auth/login", json={"email": "user@example.com", "password": "UserPass123"})
    user_token = user_login_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 3. GET /users/ (requires admin role)
    # Fails for unauthenticated
    response = await client.get("/users/")
    assert response.status_code == 401
    
    # Fails for regular user (403 Forbidden)
    response = await client.get("/users/", headers=user_headers)
    assert response.status_code == 403
    
    # Succeeds for admin
    response = await client.get("/users/", headers=admin_headers)
    assert response.status_code == 200
    users_list = response.json()
    assert len(users_list) == 2
    
    # 4. PUT /users/me (update details)
    update_payload = {
        "name": "Updated Regular User",
        "gender": "female",
        "pincode": "654321"
    }
    response = await client.put("/users/me", json=update_payload, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Regular User"
    assert data["gender"] == "female"
    assert data["pincode"] == "654321"
    
    # 5. PUT /users/{user_id}/role (admin changes user's role)
    # Fails for regular user
    role_payload = {"role": "admin"}
    response = await client.put(f"/users/{regular_user.id}/role", json=role_payload, headers=user_headers)
    assert response.status_code == 403
    
    # Succeeds for admin
    response = await client.put(f"/users/{regular_user.id}/role", json=role_payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"

async def test_products_crud_flow(client: AsyncClient, db_session):
    # 1. GET /products/ - should be empty initially
    response = await client.get("/products/")
    assert response.status_code == 200
    assert response.json() == []
    
    # 2. POST /products/ - create a product
    product_payload = {
        "name": "Awesome Laptop",
        "price": 999.99,
        "special_price": 899.99,
        "stock": 50,
        "category": "Electronics",
        "description": "An incredibly fast laptop.",
        "images": ["image_url_1.png", "image_url_2.png"]
    }
    response = await client.post("/products/", json=product_payload)
    assert response.status_code == 201
    created_product = response.json()
    assert created_product["id"] is not None
    assert created_product["name"] == "Awesome Laptop"
    assert created_product["images"] == ["image_url_1.png", "image_url_2.png"]
    
    product_id = created_product["id"]
    
    # 3. GET /products/{id} - get product by id
    response = await client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Awesome Laptop"
    
    # GET with invalid id should fail 404
    response = await client.get("/products/99999")
    assert response.status_code == 404
    
    # 4. GET /products/ - verify it lists the product
    response = await client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == product_id
    
    # 5. PUT /products/{id} - update the product
    update_payload = {
        "price": 949.99,
        "stock": 45
    }
    response = await client.put(f"/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["price"] == 949.99
    assert updated_product["stock"] == 45
    
    # 6. DELETE /products/{id} - delete the product
    response = await client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Product with id {product_id} deleted successfully"
    
    # Verify GET now returns 404
    response = await client.get(f"/products/{product_id}")
    assert response.status_code == 404
