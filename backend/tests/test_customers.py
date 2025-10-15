"""
Tests for customer endpoints.
"""

import pytest
from httpx import AsyncClient

from app.models.customer import Customer


@pytest.mark.asyncio
class TestCustomerEndpoints:
    """Test customer API endpoints."""
    
    async def test_create_customer(self, client: AsyncClient):
        """Test creating a new customer."""
        customer_data = {
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "phone": "+1-555-9999",
            "address": {
                "street": "456 Oak Ave",
                "city": "Portland",
                "state": "OR",
                "zip": "97201",
                "country": "USA",
            },
        }
        
        response = await client.post("/api/v1/customers", json=customer_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == customer_data["email"]
        assert data["first_name"] == customer_data["first_name"]
        assert "_id" in data
    
    async def test_create_duplicate_email(self, client: AsyncClient, sample_customer: Customer):
        """Test that creating a customer with duplicate email fails."""
        customer_data = {
            "email": sample_customer.email,  # Duplicate email
            "first_name": "Another",
            "last_name": "User",
        }
        
        response = await client.post("/api/v1/customers", json=customer_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    async def test_list_customers(self, client: AsyncClient, sample_customer: Customer):
        """Test listing customers with pagination."""
        response = await client.get("/api/v1/customers")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
    
    async def test_list_customers_with_search(self, client: AsyncClient):
        """Test searching customers."""
        # Create test customers
        await Customer(
            email="alice@example.com",
            first_name="Alice",
            last_name="Smith",
        ).insert()
        
        await Customer(
            email="bob@example.com",
            first_name="Bob",
            last_name="Jones",
        ).insert()
        
        # Search by first name
        response = await client.get("/api/v1/customers?search=alice")
        assert response.status_code == 200
        assert response.json()["total"] == 1
        
        # Search by email
        response = await client.get("/api/v1/customers?search=bob@")
        assert response.status_code == 200
        assert response.json()["total"] == 1
    
    async def test_get_customer(self, client: AsyncClient, sample_customer: Customer):
        """Test getting a customer by ID."""
        response = await client.get(f"/api/v1/customers/{sample_customer.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == str(sample_customer.id)
        assert data["email"] == sample_customer.email
    
    async def test_get_customer_by_email(self, client: AsyncClient, sample_customer: Customer):
        """Test getting a customer by email."""
        response = await client.get(f"/api/v1/customers/email/{sample_customer.email}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_customer.email
    
    async def test_update_customer(self, client: AsyncClient, sample_customer: Customer):
        """Test updating a customer."""
        update_data = {
            "phone": "+1-555-1111",
            "first_name": "Updated",
        }
        
        response = await client.put(
            f"/api/v1/customers/{sample_customer.id}",
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == update_data["phone"]
        assert data["first_name"] == update_data["first_name"]
    
    async def test_delete_customer(self, client: AsyncClient, sample_customer: Customer):
        """Test soft deleting a customer."""
        response = await client.delete(f"/api/v1/customers/{sample_customer.id}")
        
        assert response.status_code == 204
        
        # Verify customer is soft deleted
        customer = await Customer.get(sample_customer.id)
        assert customer.is_active is False
