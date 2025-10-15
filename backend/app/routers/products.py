"""
Product API routes.
"""

from typing import Optional
from math import ceil
from fastapi import APIRouter, HTTPException, Query, status
from beanie.operators import RegEx

from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product_data: ProductCreate) -> ProductResponse:
    """
    Create a new product in the catalog.
    
    - **name**: Product name (required)
    - **price**: Product price (required, >= 0)
    - **sku**: Stock Keeping Unit (required, unique)
    - **category**: Product category (required)
    - **stock_quantity**: Available stock (default: 0)
    """
    # Check if SKU already exists
    existing_product = await Product.find_one(Product.sku == product_data.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists",
        )
    
    # Create product
    product = Product(**product_data.model_dump())
    await product.insert()
    
    return ProductResponse(**product.model_dump())


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products with pagination and filtering",
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter products in stock"),
) -> ProductListResponse:
    """
    Retrieve a paginated list of products with optional filters.
    
    Supports filtering by:
    - **category**: Exact category match
    - **search**: Text search in name/description
    - **price range**: min_price and max_price
    - **in_stock**: Only products with stock > 0
    """
    # Build query
    query = Product.find(Product.is_active == True)
    
    if category:
        query = query.find(Product.category == category)
    
    if search:
        # Case-insensitive regex search
        query = query.find(
            {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]
            }
        )
    
    if min_price is not None:
        query = query.find(Product.price >= min_price)
    
    if max_price is not None:
        query = query.find(Product.price <= max_price)
    
    if in_stock:
        query = query.find(Product.stock_quantity > 0)
    
    # Get total count
    total = await query.count()
    
    # Calculate pagination
    pages = ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size
    
    # Fetch paginated results
    products = await query.skip(skip).limit(page_size).to_list()
    
    return ProductListResponse(
        items=[ProductResponse(**p.model_dump()) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get a product by ID",
)
async def get_product(product_id: str) -> ProductResponse:
    """
    Retrieve a specific product by its ID.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    
    return ProductResponse(**product.model_dump())


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
) -> ProductResponse:
    """
    Update an existing product.
    
    Only provided fields will be updated.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    
    # Update only provided fields
    update_data = product_data.model_dump(exclude_unset=True)
    if update_data:
        from datetime import datetime
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await product.save()
    
    return ProductResponse(**product.model_dump())


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
async def delete_product(product_id: str) -> None:
    """
    Delete a product (soft delete by setting is_active to False).
    
    For hard delete, use the force parameter.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    
    # Soft delete
    product.is_active = False
    from datetime import datetime
    product.updated_at = datetime.utcnow()
    await product.save()


@router.get(
    "/category/{category}",
    response_model=ProductListResponse,
    summary="Get products by category",
)
async def get_products_by_category(
    category: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ProductListResponse:
    """
    Retrieve all products in a specific category.
    """
    query = Product.find(
        Product.category == category,
        Product.is_active == True,
    )
    
    total = await query.count()
    pages = ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size
    
    products = await query.skip(skip).limit(page_size).to_list()
    
    return ProductListResponse(
        items=[ProductResponse(**p.model_dump()) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
