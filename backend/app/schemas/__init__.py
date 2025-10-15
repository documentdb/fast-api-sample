"""
Schemas package for API request/response validation.
"""

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    AddressSchema,
)
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderItemCreate,
    OrderItemResponse,
)

__all__ = [
    # Product schemas
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    # Customer schemas
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListResponse",
    "AddressSchema",
    # Order schemas
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderListResponse",
    "OrderItemCreate",
    "OrderItemResponse",
]
