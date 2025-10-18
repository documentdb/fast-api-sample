"""
Review schemas for API request/response validation.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    
    product_id: str = Field(..., description="Product ID to review")
    customer_email: EmailStr
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    title: str = Field(..., min_length=1, max_length=100)
    comment: str = Field(..., min_length=10, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "customer_email": "john@example.com",
                "rating": 5,
                "title": "Great product!",
                "comment": "This product exceeded my expectations. Very satisfied."
            }
        }


class ReviewUpdate(BaseModel):
    """Schema for updating a review."""
    
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)


class ReviewResponse(BaseModel):
    """Schema for review response."""
    
    id: str = Field(alias="_id")
    product_id: str
    customer_email: str
    rating: int
    title: str
    comment: str
    helpful_count: int
    verified_purchase: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class ReviewListResponse(BaseModel):
    """Schema for paginated review list."""
    
    items: list[ReviewResponse]
    total: int
    page: int
    page_size: int
    pages: int
    average_rating: Optional[float] = None