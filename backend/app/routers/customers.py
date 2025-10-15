"""
Customer API routes.
"""

from math import ceil
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
)
async def create_customer(customer_data: CustomerCreate) -> CustomerResponse:
    """
    Create a new customer account.
    
    - **email**: Customer email (required, unique)
    - **first_name**: First name (required)
    - **last_name**: Last name (required)
    - **phone**: Phone number (optional)
    - **address**: Shipping address (optional)
    """
    # Check if email already exists
    existing_customer = await Customer.find_one(Customer.email == customer_data.email)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with email '{customer_data.email}' already exists",
        )
    
    # Create customer
    customer = Customer(**customer_data.model_dump())
    await customer.insert()
    
    return CustomerResponse(**customer.model_dump())


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="List customers with pagination",
)
async def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
) -> CustomerListResponse:
    """
    Retrieve a paginated list of customers.
    
    Supports:
    - **search**: Text search in name and email fields
    """
    # Build query
    query = Customer.find(Customer.is_active == True)
    
    if search:
        # Case-insensitive search in name and email
        query = query.find(
            {
                "$or": [
                    {"email": {"$regex": search, "$options": "i"}},
                    {"first_name": {"$regex": search, "$options": "i"}},
                    {"last_name": {"$regex": search, "$options": "i"}},
                ]
            }
        )
    
    # Get total count
    total = await query.count()
    
    # Calculate pagination
    pages = ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size
    
    # Fetch paginated results
    customers = await query.skip(skip).limit(page_size).to_list()
    
    return CustomerListResponse(
        items=[CustomerResponse(**c.model_dump()) for c in customers],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get a customer by ID",
)
async def get_customer(customer_id: str) -> CustomerResponse:
    """
    Retrieve a specific customer by their ID.
    """
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID '{customer_id}' not found",
        )
    
    return CustomerResponse(**customer.model_dump())


@router.get(
    "/email/{email}",
    response_model=CustomerResponse,
    summary="Get a customer by email",
)
async def get_customer_by_email(email: str) -> CustomerResponse:
    """
    Retrieve a customer by their email address.
    """
    customer = await Customer.find_one(Customer.email == email)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with email '{email}' not found",
        )
    
    return CustomerResponse(**customer.model_dump())


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update a customer",
)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
) -> CustomerResponse:
    """
    Update an existing customer.
    
    Only provided fields will be updated.
    """
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID '{customer_id}' not found",
        )
    
    # Update only provided fields
    update_data = customer_data.model_dump(exclude_unset=True)
    if update_data:
        from datetime import datetime
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        await customer.save()
    
    return CustomerResponse(**customer.model_dump())


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a customer",
)
async def delete_customer(customer_id: str) -> None:
    """
    Delete a customer account (soft delete by setting is_active to False).
    """
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID '{customer_id}' not found",
        )
    
    # Soft delete
    customer.is_active = False
    from datetime import datetime
    customer.updated_at = datetime.utcnow()
    await customer.save()
