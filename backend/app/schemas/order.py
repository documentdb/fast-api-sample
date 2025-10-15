"""
Order schemas for API request/response validation.
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.models.order import OrderStatus


# Request schemas
class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""
    
    product_id: str
    quantity: int = Field(gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439012",
                "quantity": 2
            }
        }


class AddressSchema(BaseModel):
    """Shipping address schema."""
    
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    state: str = Field(min_length=2, max_length=2)
    zip: str = Field(min_length=5, max_length=10)
    country: str = Field(default="USA")


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    
    customer_id: str
    items: List[OrderItemCreate] = Field(min_length=1)
    shipping_address: AddressSchema
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "507f1f77bcf86cd799439011",
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439012",
                        "quantity": 1
                    }
                ],
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                    "country": "USA"
                }
            }
        }


class OrderUpdate(BaseModel):
    """Schema for updating an order."""
    
    status: Optional[OrderStatus] = None
    tracking_number: Optional[str] = None


# Response schemas
class OrderItemResponse(BaseModel):
    """Schema for order item in response."""
    
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    """Schema for order response."""
    
    id: str = Field(alias="_id")
    customer_id: str
    customer_email: EmailStr
    items: List[OrderItemResponse]
    status: OrderStatus
    total_amount: Decimal
    shipping_address: AddressSchema
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439013",
                "customer_id": "507f1f77bcf86cd799439011",
                "customer_email": "john.doe@example.com",
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439012",
                        "product_name": "Wireless Headphones",
                        "quantity": 1,
                        "unit_price": 199.99,
                        "subtotal": 199.99
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
                },
                "tracking_number": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "shipped_at": None,
                "delivered_at": None
            }
        }


class OrderListResponse(BaseModel):
    """Schema for paginated order list response."""
    
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 30,
                "page": 1,
                "page_size": 20,
                "pages": 2
            }
        }
