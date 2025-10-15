"""
Product model for DocumentDB.

Represents products in the e-commerce catalog.
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from beanie import Document, Indexed
from pydantic import Field, field_validator
from bson import Decimal128


class Product(Document):
    """Product document model."""
    
    name: Indexed(str)  # Indexed for faster searches
    description: str
    price: Decimal = Field(ge=0, description="Product price must be non-negative")
    sku: Indexed(str, unique=True)  # Stock Keeping Unit - unique identifier
    category: Indexed(str)
    tags: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(ge=0, default=0)
    is_active: bool = Field(default=True)
    image_url: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Convert price to Decimal, handling Decimal128 from MongoDB."""
        if isinstance(v, Decimal128):
            return Decimal(str(v.to_decimal()))
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    class Settings:
        name = "products"
        indexes = [
            "name",
            "sku",
            "category",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 199.99,
                "sku": "WH-1000XM4",
                "category": "Electronics",
                "tags": ["audio", "wireless", "noise-cancelling"],
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/images/headphones.jpg"
            }
        }
