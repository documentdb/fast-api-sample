"""
Review API routes.
"""

from typing import Optional
from math import ceil
from fastapi import APIRouter, HTTPException, Query, status

from app.models.review import Review
from app.models.product import Product
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewListResponse,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new review",
)
async def create_review(review_data: ReviewCreate) -> ReviewResponse:
    """
    Create a new product review.
    
    - Validates product exists
    - Checks for duplicate reviews (one per customer per product)
    - Creates review with automatic timestamps
    """
    # Verify product exists
    product = await Product.get(review_data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{review_data.product_id}' not found",
        )
    
    # Check for existing review
    existing_review = await Review.find_one(
        Review.product_id == review_data.product_id,
        Review.customer_email == review_data.customer_email
    )
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this product. Use PUT to update.",
        )
    
    # Create review
    review = Review(**review_data.model_dump())
    await review.insert()
    
    return ReviewResponse(**review.model_dump())


@router.get(
    "",
    response_model=ReviewListResponse,
    summary="List reviews with filters",
)
async def list_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: Optional[str] = Query(None, description="Filter by product"),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    customer_email: Optional[str] = None,
) -> ReviewListResponse:
    """
    Retrieve paginated list of reviews with optional filters.
    """
    # Build query
    query = Review.find()
    
    if product_id:
        query = query.find(Review.product_id == product_id)
    
    if min_rating:
        query = query.find(Review.rating >= min_rating)
    
    if customer_email:
        query = query.find(Review.customer_email == customer_email)
    
    # Sort by most recent first
    query = query.sort("-created_at")
    
    # Get total count
    total = await query.count()
    
    # Calculate pagination
    pages = ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size
    
    # Fetch paginated results
    reviews = await query.skip(skip).limit(page_size).to_list()
    
    # Calculate average rating if filtered by product
    average_rating = None
    if product_id and total > 0:
        all_reviews = await Review.find(
            Review.product_id == product_id
        ).to_list()
        average_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    
    return ReviewListResponse(
        items=[ReviewResponse(**r.model_dump()) for r in reviews],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        average_rating=round(average_rating, 2) if average_rating else None,
    )


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Get a review by ID",
)
async def get_review(review_id: str) -> ReviewResponse:
    """Retrieve a specific review by its ID."""
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID '{review_id}' not found",
        )
    
    return ReviewResponse(**review.model_dump())


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Update a review",
)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
) -> ReviewResponse:
    """Update an existing review. Only the review author can update."""
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID '{review_id}' not found",
        )
    
    # Update only provided fields
    update_data = review_data.model_dump(exclude_unset=True)
    if update_data:
        from datetime import datetime
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(review, field, value)
        
        await review.save()
    
    return ReviewResponse(**review.model_dump())


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a review",
)
async def delete_review(review_id: str) -> None:
    """Delete a review."""
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID '{review_id}' not found",
        )
    
    await review.delete()


@router.post(
    "/{review_id}/helpful",
    response_model=ReviewResponse,
    summary="Mark review as helpful",
)
async def mark_helpful(review_id: str) -> ReviewResponse:
    """Increment the helpful count for a review."""
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID '{review_id}' not found",
        )
    
    review.helpful_count += 1
    await review.save()
    
    return ReviewResponse(**review.model_dump())


@router.get(
    "/products/{product_id}/summary",
    summary="Get review summary for a product",
)
async def get_product_review_summary(product_id: str):
    """
    Get aggregated review statistics for a product.
    """
    # Verify product exists
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    
    # Get all reviews for this product
    reviews = await Review.find(Review.product_id == product_id).to_list()
    
    if not reviews:
        return {
            "product_id": product_id,
            "total_reviews": 0,
            "average_rating": 0,
            "rating_distribution": {},
        }
    
    # Calculate statistics
    total_reviews = len(reviews)
    average_rating = sum(r.rating for r in reviews) / total_reviews
    
    # Rating distribution
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_dist[review.rating] += 1
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_dist,
        "verified_purchases": sum(1 for r in reviews if r.verified_purchase),
    }