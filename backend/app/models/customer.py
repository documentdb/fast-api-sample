"""
Customer model for DocumentDB.

Represents customers in the e-commerce system.
"""

from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field, EmailStr


class Customer(Document):
    """Customer document model."""
    
    email: Indexed(EmailStr, unique=True)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    
    # Address information (embedded document)
    address: Optional[dict] = Field(
        default=None,
        description="Customer address with street, city, state, zip, country"
    )
    
    # Account status
    is_active: bool = Field(default=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "customers"
        indexes = [
            "email",
        ]
    
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
