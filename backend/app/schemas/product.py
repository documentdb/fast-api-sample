"""
Product schemas for API request/response validation.
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


# Request schemas
class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(ge=0)
    sku: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    tags: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(ge=0, default=0)
    is_active: bool = True
    image_url: Optional[str] = None
    
    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Convert price to Decimal."""
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Headphones",
                "description": "Premium noise-cancelling wireless headphones",
                "price": 199.99,
                "sku": "WH-1000XM4",
                "category": "Electronics",
                "tags": ["audio", "wireless", "noise-cancelling"],
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/headphones.jpg"
            }
        }


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    
    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Convert price to Decimal."""
        if v is not None and isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


# Response schemas
class ProductResponse(BaseModel):
    """Schema for product response."""
    
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    price: Decimal
    sku: str
    category: str
    tags: List[str] = []
    stock_quantity: int
    is_active: bool
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Wireless Headphones",
                "description": "Premium noise-cancelling wireless headphones",
                "price": 199.99,
                "sku": "WH-1000XM4",
                "category": "Electronics",
                "tags": ["audio", "wireless", "noise-cancelling"],
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/headphones.jpg",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "pages": 5
            }
        }
