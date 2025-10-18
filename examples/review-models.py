"""
Review model for product reviews.
"""

from typing import Optional
from datetime import datetime
from beanie import Document, Indexed, Link
from pydantic import Field, field_validator

from app.models.product import Product


class Review(Document):
    """Product review document model."""
    
    product_id: Indexed(str)  # Reference to product
    customer_email: Indexed(str)
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    title: str = Field(min_length=1, max_length=100)
    comment: str = Field(min_length=1, max_length=1000)
    helpful_count: int = Field(ge=0, default=0)
    verified_purchase: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("comment")
    @classmethod
    def validate_comment_content(cls, v: str) -> str:
        """Basic profanity filter."""
        # Simple example - in production use a proper library
        forbidden_words = ["spam", "fake", "scam"]
        lower_comment = v.lower()
        
        for word in forbidden_words:
            if word in lower_comment:
                raise ValueError(f"Comment contains inappropriate content")
        
        return v
    
    class Settings:
        name = "reviews"
        indexes = [
            "product_id",
            "customer_email",
            "rating",
            [("product_id", 1), ("rating", -1)],  # Compound index
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "customer_email": "john@example.com",
                "rating": 5,
                "title": "Excellent product!",
                "comment": "Works perfectly, highly recommended.",
                "verified_purchase": True
            }
        }