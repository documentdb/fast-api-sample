"""
Order model for DocumentDB.

Represents customer orders with items and status tracking.
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from beanie import Document, Indexed, Link
from pydantic import Field, field_validator

from app.models.customer import Customer


class OrderStatus(str, Enum):
    """Order status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(Document):
    """Individual item in an order (embedded document)."""
    
    product_id: str = Field(description="Reference to Product._id")
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    
    @field_validator("unit_price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Convert price to Decimal."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate item subtotal."""
        return self.unit_price * self.quantity


class Order(Document):
    """Order document model."""
    
    # Customer reference (can use Link for referential integrity)
    customer_id: str = Field(description="Reference to Customer._id")
    customer_email: Indexed(str)  # Denormalized for faster queries
    
    # Order items
    items: List[OrderItem] = Field(min_length=1)
    
    # Order details
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: Decimal = Field(ge=0)
    
    # Shipping information
    shipping_address: dict = Field(
        description="Shipping address with street, city, state, zip, country"
    )
    
    # Tracking
    tracking_number: Optional[str] = None
    
    # Metadata
    created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    @field_validator("total_amount", mode="before")
    @classmethod
    def validate_total(cls, v):
        """Convert total to Decimal."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    def calculate_total(self) -> Decimal:
        """Calculate total from items."""
        return sum(item.subtotal for item in self.items)
    
    class Settings:
        name = "orders"
        indexes = [
            "customer_email",
            "status",
            "created_at",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "507f1f77bcf86cd799439011",
                "customer_email": "john.doe@example.com",
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439012",
                        "product_name": "Wireless Headphones",
                        "quantity": 1,
                        "unit_price": 199.99
                    }
                ],
                "status": "pending",
                "total_amount": 199.99,
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                    "country": "USA"
                }
            }
        }
