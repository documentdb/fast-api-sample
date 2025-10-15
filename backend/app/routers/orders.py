"""
Order API routes.
"""

from math import ceil
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderItemResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
async def create_order(order_data: OrderCreate) -> OrderResponse:
    """
    Create a new order.
    
    - **customer_id**: ID of the customer placing the order
    - **items**: List of products and quantities
    - **shipping_address**: Delivery address
    
    The order total is automatically calculated from product prices and quantities.
    Stock quantities are updated when the order is created.
    """
    # Verify customer exists
    customer = await Customer.get(order_data.customer_id)
    if not customer or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active customer with ID '{order_data.customer_id}' not found",
        )
    
    # Process order items
    order_items = []
    total_amount = 0
    
    for item_data in order_data.items:
        # Get product
        product = await Product.get(item_data.product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active product with ID '{item_data.product_id}' not found",
            )
        
        # Check stock availability
        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product '{product.name}'. "
                       f"Available: {product.stock_quantity}, Requested: {item_data.quantity}",
            )
        
        # Create order item
        order_item = OrderItem(
            product_id=str(product.id),
            product_name=product.name,
            quantity=item_data.quantity,
            unit_price=product.price,
        )
        order_items.append(order_item)
        total_amount += order_item.subtotal
        
        # Update product stock
        product.stock_quantity -= item_data.quantity
        product.updated_at = datetime.utcnow()
        await product.save()
    
    # Create order
    order = Order(
        customer_id=str(customer.id),
        customer_email=customer.email,
        items=order_items,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address.model_dump(),
    )
    await order.insert()
    
    # Prepare response
    return OrderResponse(
        **order.model_dump(),
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
    )


@router.get(
    "",
    response_model=OrderListResponse,
    summary="List orders with pagination and filtering",
)
async def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
) -> OrderListResponse:
    """
    Retrieve a paginated list of orders.
    
    Supports filtering by:
    - **customer_id**: Get orders for a specific customer
    - **status**: Filter by order status (pending, processing, shipped, delivered, cancelled)
    """
    # Build query
    query = Order.find()
    
    if customer_id:
        query = query.find(Order.customer_id == customer_id)
    
    if status:
        query = query.find(Order.status == status)
    
    # Get total count
    total = await query.count()
    
    # Calculate pagination
    pages = ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size
    
    # Fetch paginated results (sort by created_at descending)
    orders = await query.sort(-Order.created_at).skip(skip).limit(page_size).to_list()
    
    # Convert to response format
    order_responses = []
    for order in orders:
        order_responses.append(
            OrderResponse(
                **order.model_dump(),
                items=[
                    OrderItemResponse(
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        subtotal=item.subtotal,
                    )
                    for item in order.items
                ],
            )
        )
    
    return OrderListResponse(
        items=order_responses,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get an order by ID",
)
async def get_order(order_id: str) -> OrderResponse:
    """
    Retrieve a specific order by its ID.
    """
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found",
        )
    
    return OrderResponse(
        **order.model_dump(),
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
    )


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update an order",
)
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
) -> OrderResponse:
    """
    Update an existing order.
    
    Currently supports updating:
    - **status**: Change order status
    - **tracking_number**: Add/update tracking information
    """
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found",
        )
    
    # Update only provided fields
    update_data = order_data.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # Update timestamp fields based on status
        if "status" in update_data:
            if update_data["status"] == OrderStatus.SHIPPED and not order.shipped_at:
                update_data["shipped_at"] = datetime.utcnow()
            elif update_data["status"] == OrderStatus.DELIVERED and not order.delivered_at:
                update_data["delivered_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(order, field, value)
        
        await order.save()
    
    return OrderResponse(
        **order.model_dump(),
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
    )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel an order",
)
async def cancel_order(order_id: str) -> None:
    """
    Cancel an order (sets status to CANCELLED).
    
    Stock quantities are restored when an order is cancelled,
    unless it has already been shipped or delivered.
    """
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found",
        )
    
    # Can't cancel shipped or delivered orders
    if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status '{order.status}'",
        )
    
    # Restore stock quantities
    for item in order.items:
        product = await Product.get(item.product_id)
        if product:
            product.stock_quantity += item.quantity
            product.updated_at = datetime.utcnow()
            await product.save()
    
    # Update order status
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()
    await order.save()
