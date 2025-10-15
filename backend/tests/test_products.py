"""
Tests for product endpoints.
"""

import pytest
from httpx import AsyncClient

from app.models.product import Product


@pytest.mark.asyncio
class TestProductEndpoints:
    """Test product API endpoints."""
    
    async def test_create_product(self, client: AsyncClient):
        """Test creating a new product."""
        product_data = {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": 29.99,
            "sku": "MOUSE-001",
            "category": "Electronics",
            "stock_quantity": 100,
        }
        
        response = await client.post("/api/v1/products", json=product_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["sku"] == product_data["sku"]
        assert "_id" in data
    
    async def test_create_duplicate_sku(self, client: AsyncClient, sample_product: Product):
        """Test that creating a product with duplicate SKU fails."""
        product_data = {
            "name": "Another Product",
            "price": 19.99,
            "sku": sample_product.sku,  # Duplicate SKU
            "category": "Electronics",
        }
        
        response = await client.post("/api/v1/products", json=product_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    async def test_list_products(self, client: AsyncClient, sample_product: Product):
        """Test listing products with pagination."""
        response = await client.get("/api/v1/products")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
    
    async def test_list_products_with_filters(self, client: AsyncClient):
        """Test listing products with filters."""
        # Create test products
        await Product(
            name="Laptop",
            price=999.99,
            sku="LAP-001",
            category="Electronics",
            stock_quantity=5,
        ).insert()
        
        await Product(
            name="Mouse",
            price=29.99,
            sku="MOU-001",
            category="Electronics",
            stock_quantity=0,
        ).insert()
        
        # Test category filter
        response = await client.get("/api/v1/products?category=Electronics")
        assert response.status_code == 200
        assert response.json()["total"] == 2
        
        # Test in_stock filter
        response = await client.get("/api/v1/products?in_stock=true")
        assert response.status_code == 200
        assert response.json()["total"] == 1
        
        # Test search
        response = await client.get("/api/v1/products?search=laptop")
        assert response.status_code == 200
        assert response.json()["total"] == 1
    
    async def test_get_product(self, client: AsyncClient, sample_product: Product):
        """Test getting a product by ID."""
        response = await client.get(f"/api/v1/products/{sample_product.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == str(sample_product.id)
        assert data["name"] == sample_product.name
    
    async def test_get_nonexistent_product(self, client: AsyncClient):
        """Test getting a product that doesn't exist."""
        fake_id = "507f1f77bcf86cd799439011"
        response = await client.get(f"/api/v1/products/{fake_id}")
        
        assert response.status_code == 404
    
    async def test_update_product(self, client: AsyncClient, sample_product: Product):
        """Test updating a product."""
        update_data = {
            "price": 149.99,
            "stock_quantity": 20,
        }
        
        response = await client.put(
            f"/api/v1/products/{sample_product.id}",
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert float(data["price"]) == update_data["price"]
        assert data["stock_quantity"] == update_data["stock_quantity"]
    
    async def test_delete_product(self, client: AsyncClient, sample_product: Product):
        """Test soft deleting a product."""
        response = await client.delete(f"/api/v1/products/{sample_product.id}")
        
        assert response.status_code == 204
        
        # Verify product is soft deleted (is_active = False)
        product = await Product.get(sample_product.id)
        assert product.is_active is False
    
    async def test_get_products_by_category(self, client: AsyncClient):
        """Test getting products by category."""
        # Create products in different categories
        await Product(
            name="Laptop",
            price=999.99,
            sku="LAP-001",
            category="Electronics",
        ).insert()
        
        await Product(
            name="Chair",
            price=199.99,
            sku="CHR-001",
            category="Furniture",
        ).insert()
        
        response = await client.get("/api/v1/products/category/Electronics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "Electronics"
