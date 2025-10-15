"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from httpx import AsyncClient

from app.main import app
from app.core.config import settings
from app.models import Product, Customer, Order


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """
    Initialize test database.
    
    Uses a separate test database to avoid affecting production data.
    """
    # Create test database connection
    test_db_name = "documentdb_test"
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize Beanie with test database
    await init_beanie(
        database=client[test_db_name],
        document_models=[Product, Customer, Order],
    )
    
    yield client
    
    # Cleanup: Drop test database after tests
    await client.drop_database(test_db_name)
    client.close()


@pytest.fixture(autouse=True)
async def clean_db(test_db):
    """
    Clean database before each test.
    """
    # Clear all collections before each test
    await Product.delete_all()
    await Customer.delete_all()
    await Order.delete_all()
    
    yield
    
    # Optional: cleanup after test
    # await Product.delete_all()
    # await Customer.delete_all()
    # await Order.delete_all()


@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing the API.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def sample_product() -> Product:
    """
    Create a sample product for testing.
    """
    product = Product(
        name="Test Product",
        description="A test product",
        price=99.99,
        sku="TEST-001",
        category="Electronics",
        stock_quantity=10,
    )
    await product.insert()
    return product


@pytest.fixture
async def sample_customer() -> Customer:
    """
    Create a sample customer for testing.
    """
    customer = Customer(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        phone="+1-555-0123",
        address={
            "street": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "country": "USA",
        },
    )
    await customer.insert()
    return customer


@pytest.fixture
async def sample_order(sample_customer: Customer, sample_product: Product) -> Order:
    """
    Create a sample order for testing.
    """
    from app.models.order import OrderItem
    
    order = Order(
        customer_id=str(sample_customer.id),
        customer_email=sample_customer.email,
        items=[
            OrderItem(
                product_id=str(sample_product.id),
                product_name=sample_product.name,
                quantity=2,
                unit_price=sample_product.price,
            )
        ],
        total_amount=sample_product.price * 2,
        shipping_address={
            "street": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "country": "USA",
        },
    )
    await order.insert()
    return order
