"""
Script to load sample data into the database.

Run this script to populate the database with sample products, customers, and orders.
"""

import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from decimal import Decimal

# Import models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import Product, Customer, Order
from app.models.order import OrderItem, OrderStatus
from app.core.config import settings


async def load_sample_data():
    """Load sample data into DocumentDB."""
    
    print("🔌 Connecting to DocumentDB...")
    client = AsyncIOMotorClient(settings.DOCUMENTDB_URL)
    
    # Initialize Beanie
    await init_beanie(
        database=client[settings.DOCUMENTDB_DB_NAME],
        document_models=[Product, Customer, Order],
    )
    
    print("✅ Connected successfully!\n")
    
    # Clear existing data
    print("🗑️  Clearing existing data...")
    await Product.delete_all()
    await Customer.delete_all()
    await Order.delete_all()
    print("✅ Data cleared\n")
    
    # Load products from JSON file
    print("📦 Loading products from sample_products.json...")
    script_dir = Path(__file__).parent
    products_file = script_dir / "sample_products.json"
    
    with open(products_file, 'r') as f:
        products_data = json.load(f)
    
    products = []
    for product_data in products_data:
        # Convert price to Decimal
        product_data['price'] = Decimal(str(product_data['price']))
        product = Product(**product_data)
        await product.insert()
        products.append(product)
    
    print(f"✅ Created {len(products)} products\n")
    
    # Load customers from JSON file
    print("👥 Loading customers from sample_customers.json...")
    customers_file = script_dir / "sample_customers.json"
    
    with open(customers_file, 'r') as f:
        customers_data = json.load(f)
    
    customers = []
    for customer_data in customers_data:
        # Fix address field name if needed (postal_code -> zip)
        if 'address' in customer_data and 'postal_code' in customer_data['address']:
            customer_data['address']['zip'] = customer_data['address'].pop('postal_code')
        
        customer = Customer(**customer_data)
        await customer.insert()
        customers.append(customer)
    
    print(f"✅ Created {len(customers)} customers\n")
    
    # Create sample orders
    print("🛒 Creating sample orders...")
    
    # Order 1: Alice buys headphones and keyboard
    order1 = Order(
        customer_id=str(customers[0].id),
        customer_email=customers[0].email,
        items=[
            OrderItem(
                product_id=str(products[0].id),
                product_name=products[0].name,
                quantity=1,
                unit_price=products[0].price,
            ),
            OrderItem(
                product_id=str(products[3].id),
                product_name=products[3].name,
                quantity=1,
                unit_price=products[3].price,
            ),
        ],
        total_amount=products[0].price + products[3].price,
        shipping_address=customers[0].address,
        status=OrderStatus.DELIVERED,
    )
    await order1.insert()
    
    # Order 2: Bob buys a standing desk
    order2 = Order(
        customer_id=str(customers[1].id),
        customer_email=customers[1].email,
        items=[
            OrderItem(
                product_id=str(products[4].id),
                product_name=products[4].name,
                quantity=1,
                unit_price=products[4].price,
            ),
        ],
        total_amount=products[4].price,
        shipping_address=customers[1].address,
        status=OrderStatus.SHIPPED,
        tracking_number="1Z999AA10123456784",
    )
    await order2.insert()
    
    # Order 3: Carol buys monitor and mouse
    order3 = Order(
        customer_id=str(customers[2].id),
        customer_email=customers[2].email,
        items=[
            OrderItem(
                product_id=str(products[2].id),
                product_name=products[2].name,
                quantity=1,
                unit_price=products[2].price,
            ),
            OrderItem(
                product_id=str(products[5].id),
                product_name=products[5].name,
                quantity=2,
                unit_price=products[5].price,
            ),
        ],
        total_amount=products[2].price + (products[5].price * 2),
        shipping_address=customers[2].address,
        status=OrderStatus.PENDING,
    )
    await order3.insert()
    
    print("✅ Created 3 sample orders\n")
    
    # Summary
    print("=" * 50)
    print("✨ Sample data loaded successfully!")
    print("=" * 50)
    print(f"Products:  {len(products)}")
    print(f"Customers: {len(customers)}")
    print(f"Orders:    3")
    print("\n🚀 Visit http://localhost:8000/docs to explore the API!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(load_sample_data())
