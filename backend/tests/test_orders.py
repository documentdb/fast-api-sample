"""
Tests for order endpoints.
"""

import pytest
from httpx import AsyncClient

from app.models import Product, Customer, Order
from app.models.order import OrderStatus


@pytest.mark.asyncio
class TestOrderEndpoints:
    """Test order API endpoints."""
    
    async def test_create_order(
        self,
        client: AsyncClient,
        sample_customer: Customer,
        sample_product: Product,
    ):
        """Test creating a new order."""
        initial_stock = sample_product.stock_quantity
        
        order_data = {
            "customer_id": str(sample_customer.id),
            "items": [
                {
                    "product_id": str(sample_product.id),
                    "quantity": 2,
                }
            ],
            "shipping_address": {
                "street": "789 Delivery Ln",
                "city": "Seattle",
                "state": "WA",
                "zip": "98101",
                "country": "USA",
            },
        }
        
        response = await client.post("/api/v1/orders", json=order_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == order_data["customer_id"]
        assert len(data["items"]) == 1
        assert data["status"] == OrderStatus.PENDING
        
        # Verify stock was updated
        updated_product = await Product.get(sample_product.id)
        assert updated_product.stock_quantity == initial_stock - 2
    
    async def test_create_order_insufficient_stock(
        self,
        client: AsyncClient,
        sample_customer: Customer,
        sample_product: Product,
    ):
        """Test creating an order with insufficient stock."""
        order_data = {
            "customer_id": str(sample_customer.id),
            "items": [
                {
                    "product_id": str(sample_product.id),
                    "quantity": 999,  # More than available
                }
            ],
            "shipping_address": {
                "street": "789 Delivery Ln",
                "city": "Seattle",
                "state": "WA",
                "zip": "98101",
                "country": "USA",
            },
        }
        
        response = await client.post("/api/v1/orders", json=order_data)
        
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
    
    async def test_create_order_nonexistent_customer(
        self,
        client: AsyncClient,
        sample_product: Product,
    ):
        """Test creating an order with a nonexistent customer."""
        order_data = {
            "customer_id": "507f1f77bcf86cd799439011",  # Fake ID
            "items": [
                {
                    "product_id": str(sample_product.id),
                    "quantity": 1,
                }
            ],
            "shipping_address": {
                "street": "789 Delivery Ln",
                "city": "Seattle",
                "state": "WA",
                "zip": "98101",
                "country": "USA",
            },
        }
        
        response = await client.post("/api/v1/orders", json=order_data)
        
        assert response.status_code == 404
        assert "customer" in response.json()["detail"].lower()
    
    async def test_list_orders(self, client: AsyncClient, sample_order: Order):
        """Test listing orders."""
        response = await client.get("/api/v1/orders")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
    
    async def test_list_orders_by_customer(
        self,
        client: AsyncClient,
        sample_customer: Customer,
        sample_order: Order,
    ):
        """Test filtering orders by customer."""
        response = await client.get(
            f"/api/v1/orders?customer_id={sample_customer.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(
            item["customer_id"] == str(sample_customer.id)
            for item in data["items"]
        )
    
    async def test_list_orders_by_status(self, client: AsyncClient):
        """Test filtering orders by status."""
        # Create orders with different statuses
        customer = await Customer(
            email="ordertest@example.com",
            first_name="Order",
            last_name="Test",
        ).insert()
        
        product = await Product(
            name="Test Product",
            price=10.00,
            sku="TEST-ORD",
            category="Test",
            stock_quantity=100,
        ).insert()
        
        from app.models.order import OrderItem
        
        # Pending order
        await Order(
            customer_id=str(customer.id),
            customer_email=customer.email,
            items=[
                OrderItem(
                    product_id=str(product.id),
                    product_name=product.name,
                    quantity=1,
                    unit_price=product.price,
                )
            ],
            total_amount=10.00,
            shipping_address={"street": "123 St", "city": "City", "state": "CA", "zip": "12345", "country": "USA"},
            status=OrderStatus.PENDING,
        ).insert()
        
        # Shipped order
        await Order(
            customer_id=str(customer.id),
            customer_email=customer.email,
            items=[
                OrderItem(
                    product_id=str(product.id),
                    product_name=product.name,
                    quantity=1,
                    unit_price=product.price,
                )
            ],
            total_amount=10.00,
            shipping_address={"street": "123 St", "city": "City", "state": "CA", "zip": "12345", "country": "USA"},
            status=OrderStatus.SHIPPED,
        ).insert()
        
        response = await client.get("/api/v1/orders?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "pending" for item in data["items"])
    
    async def test_get_order(self, client: AsyncClient, sample_order: Order):
        """Test getting an order by ID."""
        response = await client.get(f"/api/v1/orders/{sample_order.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == str(sample_order.id)
    
    async def test_update_order_status(self, client: AsyncClient, sample_order: Order):
        """Test updating order status."""
        update_data = {
            "status": OrderStatus.SHIPPED,
            "tracking_number": "1Z999AA10123456784",
        }
        
        response = await client.put(
            f"/api/v1/orders/{sample_order.id}",
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == OrderStatus.SHIPPED
        assert data["tracking_number"] == update_data["tracking_number"]
        assert data["shipped_at"] is not None
    
    async def test_cancel_order(
        self,
        client: AsyncClient,
        sample_order: Order,
        sample_product: Product,
    ):
        """Test cancelling an order."""
        # Get initial stock
        product = await Product.get(sample_product.id)
        initial_stock = product.stock_quantity
        
        response = await client.delete(f"/api/v1/orders/{sample_order.id}")
        
        assert response.status_code == 204
        
        # Verify order is cancelled
        order = await Order.get(sample_order.id)
        assert order.status == OrderStatus.CANCELLED
        
        # Verify stock was restored
        product = await Product.get(sample_product.id)
        expected_stock = initial_stock + sample_order.items[0].quantity
        assert product.stock_quantity == expected_stock
    
    async def test_cannot_cancel_shipped_order(self, client: AsyncClient, sample_order: Order):
        """Test that shipped orders cannot be cancelled."""
        # Update order to shipped
        sample_order.status = OrderStatus.SHIPPED
        await sample_order.save()
        
        response = await client.delete(f"/api/v1/orders/{sample_order.id}")
        
        assert response.status_code == 400
        assert "Cannot cancel" in response.json()["detail"]
