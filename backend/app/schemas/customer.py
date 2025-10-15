"""
Customer schemas for API request/response validation.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Request schemas
class AddressSchema(BaseModel):
    """Address schema (embedded)."""
    
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip: Optional[str] = Field(None, min_length=5, max_length=10)
    country: str = Field(default="USA")


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""
    
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[AddressSchema] = None
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-0123",
                "address": {
                    "street": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                    "country": "USA"
                },
                "is_active": True
            }
        }


class CustomerUpdate(BaseModel):
    """Schema for updating a customer (all fields optional)."""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[AddressSchema] = None
    is_active: Optional[bool] = None


# Response schemas
class CustomerResponse(BaseModel):
    """Schema for customer response."""
    
    id: str = Field(alias="_id")
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[AddressSchema] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-0123",
                "address": {
                    "street": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                    "country": "USA"
                },
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class CustomerListResponse(BaseModel):
    """Schema for paginated customer list response."""
    
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "page_size": 20,
                "pages": 3
            }
        }
