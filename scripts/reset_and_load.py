"""
Script to reset and load sample data via the FastAPI backend.
This script deletes all existing data and loads fresh sample data.
"""

import requests
import json
from pathlib import Path

# API base URL
API_URL = "http://localhost:8000/api/v1"

def delete_all_products():
    """Delete all products."""
    print("🗑️  Deleting all existing products...")
    
    # Get all products (including those that might have errors)
    try:
        # Try to get products
        response = requests.get(f"{API_URL}/products?page=1&size=1000")
        if response.status_code == 200:
            products = response.json().get('items', [])
            deleted_count = 0
            for product in products:
                try:
                    del_response = requests.delete(f"{API_URL}/products/{product['_id']}")
                    if del_response.status_code == 204:
                        deleted_count += 1
                        print(f"  ✅ Deleted: {product.get('name', 'Unknown')}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete product: {e}")
            
            print(f"✅ Deleted {deleted_count} products\n")
        else:
            print(f"⚠️  Could not retrieve products: {response.status_code}\n")
    except Exception as e:
        print(f"⚠️  Error during deletion: {e}\n")


def delete_all_customers():
    """Delete all customers."""
    print("🗑️  Deleting all existing customers...")
    
    try:
        response = requests.get(f"{API_URL}/customers?page=1&size=1000")
        if response.status_code == 200:
            customers = response.json().get('items', [])
            deleted_count = 0
            for customer in customers:
                try:
                    del_response = requests.delete(f"{API_URL}/customers/{customer['_id']}")
                    if del_response.status_code == 204:
                        deleted_count += 1
                        print(f"  ✅ Deleted: {customer.get('email', 'Unknown')}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete customer: {e}")
            
            print(f"✅ Deleted {deleted_count} customers\n")
        else:
            print(f"⚠️  Could not retrieve customers: {response.status_code}\n")
    except Exception as e:
        print(f"⚠️  Error during deletion: {e}\n")


def load_products():
    """Load products from sample_products.json via API."""
    script_dir = Path(__file__).parent
    products_file = script_dir / "sample_products.json"
    
    print("📦 Loading products from sample_products.json...")
    
    with open(products_file, 'r') as f:
        products = json.load(f)
    
    created_count = 0
    for product in products:
        try:
            response = requests.post(f"{API_URL}/products", json=product)
            if response.status_code == 201:
                created_count += 1
                print(f"  ✅ Created: {product['name']}")
            else:
                print(f"  ❌ Failed to create {product['name']}: {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating {product['name']}: {e}")
    
    print(f"\n✨ Successfully created {created_count}/{len(products)} products!")


def load_customers():
    """Load customers from sample_customers.json via API."""
    script_dir = Path(__file__).parent
    customers_file = script_dir / "sample_customers.json"
    
    print("\n👥 Loading customers from sample_customers.json...")
    
    with open(customers_file, 'r') as f:
        customers = json.load(f)
    
    created_count = 0
    for customer in customers:
        # Fix address field name (postal_code -> zip_code)
        if 'address' in customer and 'postal_code' in customer['address']:
            customer['address']['zip_code'] = customer['address'].pop('postal_code')
        
        try:
            response = requests.post(f"{API_URL}/customers", json=customer)
            if response.status_code == 201:
                created_count += 1
                print(f"  ✅ Created: {customer['first_name']} {customer['last_name']}")
            else:
                print(f"  ❌ Failed to create {customer['first_name']} {customer['last_name']}: {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating {customer['first_name']} {customer['last_name']}: {e}")
    
    print(f"\n✨ Successfully created {created_count}/{len(customers)} customers!")


if __name__ == "__main__":
    print("=" * 70)
    print("  Sample Data Reset & Loader")
    print("=" * 70)
    print()
    
    # Delete existing data
    delete_all_products()
    delete_all_customers()
    
    # Load fresh data
    load_products()
    load_customers()
    
    print("\n" + "=" * 70)
    print("  🚀 Data reset and loading complete!")
    print("=" * 70)
    print(f"\n  Visit http://localhost/admin/products to see the products")
    print(f"  Visit http://localhost/admin/customers to see the customers\n")
