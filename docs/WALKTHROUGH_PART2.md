# FastAPI + DocumentDB: Building Modern, Intelligent APIs
## Part 2: FastAPI Deep Dive

> **Prerequisites**: Completed [Part 1: Foundation](WALKTHROUGH_PART1_FOUNDATION.md)

**Duration**: 2-3 hours  
**Difficulty**: Intermediate to Advanced

---

## 📚 Complete Walkthrough Navigation

- [Part 1: Foundation](WALKTHROUGH_PART1.md)
- **Part 2: FastAPI Deep Dive** ← You are here
- [Part 3: DocumentDB Superpowers](FASTAPI_ADVANCED_WALKTHROUGH_PART3.md)
- [Part 4: Production Ready](FASTAPI_ADVANCED_WALKTHROUGH_PART4.md)

---

## Step 4: Understanding FastAPI Architecture

### 4.1 Async/Await with Database Operations

Let's understand **why async matters** for database operations.

**Open `backend/app/routers/products.py` and examine:**

```python
@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    # Build query
    query = Product.find(Product.is_active == True)
    
    # Get total count
    total = await query.count()  # ⬅️ Async database call
    
    # Fetch paginated results
    products = await query.skip(skip).limit(page_size).to_list()  # ⬅️ Async
    
    return ProductListResponse(...)
```

**Key Points:**
- `async def` declares an async function
- `await` pauses execution until the database operation completes
- Other requests can be processed during this pause
- No thread blocking!

### 4.2 Request Lifecycle & Performance

Let's trace a request through FastAPI:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HTTP Request arrives at Uvicorn (ASGI Server)           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 2. FastAPI Router matches /api/v1/products                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 3. Pydantic validates query parameters                     │
│    - page: int (must be >= 1)                              │
│    - page_size: int (must be 1-100)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 4. Handler executes: list_products()                        │
│    - Creates Beanie query object                           │
│    - await query.count() → Releases event loop             │
│    - DocumentDB processes query via PostgreSQL             │
│    - await query.to_list() → Gets results                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 5. Pydantic serializes response to JSON                    │
│    - ProductListResponse validates structure               │
│    - Converts Decimal to float, datetime to ISO string     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ 6. HTTP Response sent back (200 OK)                        │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Code Walkthrough: Annotated Examples

Let's examine the product creation endpoint in detail:

**File: `backend/app/routers/products.py`**

```python
@router.post(
    "",
    response_model=ProductResponse,           # ⬅️ Defines expected response structure
    status_code=status.HTTP_201_CREATED,      # ⬅️ Sets HTTP status code
    summary="Create a new product",           # ⬅️ OpenAPI documentation
)
async def create_product(
    product_data: ProductCreate               # ⬅️ Request body validation
) -> ProductResponse:                         # ⬅️ Return type hint
    """
    Create a new product in the catalog.
    
    - **name**: Product name (required)
    - **price**: Product price (required, >= 0)
    - **sku**: Stock Keeping Unit (required, unique)
    - **category**: Product category (required)
    - **stock_quantity**: Available stock (default: 0)
    """
    # 1. Business logic validation
    existing_product = await Product.find_one(Product.sku == product_data.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists",
        )
    
    # 2. Create document from validated data
    product = Product(**product_data.model_dump())
    
    # 3. Insert into DocumentDB (async operation)
    await product.insert()
    
    # 4. Return serialized response
    return ProductResponse(**product.model_dump())
```

**What's happening here?**

1. **Input Validation**: `ProductCreate` schema ensures:
   - All required fields present
   - `price >= 0` (field constraint)
   - `name` length is 1-200 characters
   - Automatic type coercion (string to Decimal)

2. **Business Logic**: Check for duplicate SKU before insertion

3. **Database Operation**: Beanie's `.insert()` method:
   - Converts Python object to BSON
   - Sends to DocumentDB
   - DocumentDB stores in PostgreSQL as JSONB
   - Returns with generated `_id`

4. **Response Validation**: `ProductResponse` ensures:
   - Correct field types
   - Proper serialization (Decimal → float, datetime → ISO string)
   - Alias handling (`id` → `_id`)

### 4.4 Exercise: Benchmark Sync vs Async Queries

Let's create a performance comparison to see async in action!

**Create a new file: `backend/app/routers/benchmark.py`**

```python
"""
Benchmark endpoints to demonstrate async performance benefits.
"""

import time
import asyncio
from typing import List
from fastapi import APIRouter, HTTPException
from app.models.product import Product

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


async def fetch_product_async(product_id: str):
    """Simulate async database fetch."""
    product = await Product.get(product_id)
    return product


def fetch_product_sync_simulation(product_id: str):
    """Simulate synchronous database fetch (for comparison)."""
    # In real sync code, this would block the entire thread
    time.sleep(0.1)  # Simulate 100ms database latency
    return {"id": product_id, "name": "Product", "fetched": "sync"}


@router.get("/async-sequential")
async def benchmark_async_sequential():
    """Fetch 10 products sequentially using async."""
    start_time = time.time()
    
    # Get first 10 products
    products = await Product.find().limit(10).to_list()
    product_ids = [str(p.id) for p in products]
    
    results = []
    for product_id in product_ids:
        product = await fetch_product_async(product_id)
        results.append(product)
    
    elapsed = time.time() - start_time
    
    return {
        "method": "async_sequential",
        "products_fetched": len(results),
        "elapsed_seconds": round(elapsed, 3),
        "note": "Async but sequential - waits for each query"
    }


@router.get("/async-parallel")
async def benchmark_async_parallel():
    """Fetch 10 products in parallel using async."""
    start_time = time.time()
    
    # Get first 10 products
    products = await Product.find().limit(10).to_list()
    product_ids = [str(p.id) for p in products]
    
    # Create tasks for parallel execution
    tasks = [fetch_product_async(product_id) for product_id in product_ids]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    
    return {
        "method": "async_parallel",
        "products_fetched": len(results),
        "elapsed_seconds": round(elapsed, 3),
        "note": "Async and parallel - much faster!"
    }


@router.get("/simulate-sync")
async def benchmark_simulate_sync():
    """Simulate synchronous behavior (blocking)."""
    start_time = time.time()
    
    # Get first 10 products to get IDs
    products = await Product.find().limit(10).to_list()
    product_ids = [str(p.id) for p in products]
    
    results = []
    for product_id in product_ids:
        # This simulates blocking behavior
        result = fetch_product_sync_simulation(product_id)
        results.append(result)
    
    elapsed = time.time() - start_time
    
    return {
        "method": "simulated_sync",
        "products_fetched": len(results),
        "elapsed_seconds": round(elapsed, 3),
        "note": "Simulated sync behavior - slowest (10 x 100ms = 1+ second)"
    }


@router.get("/comparison")
async def benchmark_comparison():
    """Run all benchmarks and compare."""
    # Run each benchmark
    async_seq = await benchmark_async_sequential()
    async_par = await benchmark_async_parallel()
    sim_sync = await benchmark_simulate_sync()
    
    return {
        "benchmarks": [async_seq, async_par, sim_sync],
        "summary": {
            "async_parallel_speedup": round(
                sim_sync["elapsed_seconds"] / async_par["elapsed_seconds"], 2
            ),
            "winner": "async_parallel"
        }
    }
```

**Register the router in `backend/app/main.py`:**

```python
from app.routers import products, customers, orders, admin, benchmark

app.include_router(benchmark.router, prefix="/api/v1")
```

**Now test it!**

```powershell
# Restart the server
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs and try:
1. `/api/v1/benchmark/async-sequential`
2. `/api/v1/benchmark/async-parallel`
3. `/api/v1/benchmark/simulate-sync`
4. `/api/v1/benchmark/comparison`

**Expected Results:**
- **Simulated Sync**: ~1+ second (10 queries × 100ms each)
- **Async Sequential**: ~200-400ms (still sequential but non-blocking)
- **Async Parallel**: ~100-200ms (all queries execute concurrently)

**Key Takeaway**: Async + parallel execution = **5-10x faster** for I/O-bound operations!

---

## Step 5: Pydantic + Beanie Integration

### 5.1 Document Models vs Request/Response Schemas

Understanding the separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer                                │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │ ProductCreate    │  POST   │ ProductResponse  │        │
│  │ (Request Schema) │ ─────▶  │ (Response Schema)│        │
│  └────────┬─────────┘         └────────▲─────────┘        │
│           │                              │                  │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            │      Business Logic          │
            ▼                              │
┌─────────────────────────────────────────┼──────────────────┐
│           │      Database Layer         │                  │
│           │                              │                  │
│  ┌────────▼──────────┐        ┌─────────┴─────────┐       │
│  │     Product        │ INSERT │     Product       │       │
│  │ (Beanie Document)  │ ─────▶ │ (in DocumentDB)   │       │
│  └────────────────────┘        └───────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**File: `backend/app/schemas/product.py`** (API contracts)

```python
class ProductCreate(BaseModel):
    """Schema for creating a new product - INPUT"""
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(ge=0)
    sku: str = Field(min_length=1, max_length=100)
    # ... validates incoming JSON
```

**File: `backend/app/models/product.py`** (Database representation)

```python
class Product(Document):
    """Product document model - DATABASE"""
    name: Indexed(str)  # Creates database index
    price: Decimal
    sku: Indexed(str, unique=True)  # Enforces uniqueness at DB level
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # ... represents actual document in DocumentDB
```

**Why separate?**

1. **API Evolution**: Change request/response format without touching database schema
2. **Security**: Hide internal fields (e.g., `internal_notes`)
3. **Validation**: Different rules for create vs update
4. **Flexibility**: One document model, multiple API representations

#### 5.2 Type Safety Through the Stack

Let's trace type safety from HTTP request to database:

```python
# 1. HTTP JSON arrives
{
    "name": "USB Cable",
    "price": 19.99,
    "sku": "USB-001",
    "category": "Electronics"
}

# 2. Pydantic parses and validates (ProductCreate schema)
ProductCreate(
    name="USB Cable",           # ✅ str, length OK
    price=Decimal("19.99"),     # ✅ Decimal, >= 0
    sku="USB-001",              # ✅ str, length OK
    category="Electronics"      # ✅ str, length OK
)

# 3. Convert to Beanie Document (Product model)
product = Product(
    name="USB Cable",
    price=Decimal("19.99"),
    sku="USB-001",
    category="Electronics",
    created_at=datetime.utcnow()  # Auto-generated
)

# 4. Beanie serializes to BSON
{
    "_id": ObjectId("..."),
    "name": "USB Cable",
    "price": NumberDecimal("19.99"),
    "sku": "USB-001",
    "category": "Electronics",
    "created_at": ISODate("2025-10-16T...")
}

# 5. DocumentDB stores as JSONB in PostgreSQL
{
    "object_id": 12345,
    "document": '{"_id": ..., "name": "USB Cable", ...}'
}

# 6. Retrieved, deserialized, validated back through Pydantic (ProductResponse)
ProductResponse(
    id="507f1f77bcf86cd799439011",  # _id aliased to id
    name="USB Cable",
    price=19.99,                     # Decimal → float for JSON
    ...
)

# 7. JSON response
{
    "_id": "507f1f77bcf86cd799439011",
    "name": "USB Cable",
    "price": 19.99,
    ...
}
```

**Type safety at every layer!**

### 5.3 Custom Validators for Business Logic

Let's add advanced validation to our models:

**File: `backend/app/schemas/product.py`**

```python
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class ProductCreate(BaseModel):
    """Schema for creating a new product with advanced validation."""
    
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(ge=0)
    sku: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    tags: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(ge=0, default=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    
    @field_validator("sku")
    @classmethod
    def validate_sku_format(cls, v: str) -> str:
        """
        Ensure SKU follows format: CATEGORY-PRODUCTTYPE-###
        Example: ELEC-CABLE-001
        """
        pattern = r'^[A-Z]{4}-[A-Z]{3,10}-\d{3}$'
        if not re.match(pattern, v):
            raise ValueError(
                "SKU must follow format: XXXX-XXXXX-###"
                " (e.g., ELEC-CABLE-001)"
            )
        return v.upper()
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Ensure tags are lowercase and unique."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        
        # Convert to lowercase and remove duplicates
        unique_tags = list(set(tag.lower().strip() for tag in v))
        return unique_tags
    
    @field_validator("price")
    @classmethod
    def validate_price_precision(cls, v: Decimal) -> Decimal:
        """Ensure price has max 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price can have maximum 2 decimal places")
        return v
    
    @model_validator(mode='after')
    def validate_pricing(self):
        """Ensure selling price is higher than cost price."""
        if self.cost_price is not None and self.price <= self.cost_price:
            raise ValueError(
                f"Selling price ({self.price}) must be higher than "
                f"cost price ({self.cost_price})"
            )
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "USB-C Cable 2m",
                "description": "Durable braided charging cable",
                "price": 19.99,
                "sku": "ELEC-CABLE-001",
                "category": "Electronics",
                "tags": ["usb-c", "charging", "cable"],
                "stock_quantity": 150,
                "cost_price": 8.50
            }
        }
```

**Test the validators:**

Visit http://localhost:8000/docs and try creating products with:
- Invalid SKU: `"test-123"` → ❌ Should fail
- Valid SKU: `"ELEC-CABLE-001"` → ✅ Should pass
- Too many decimal places: `19.999` → ❌ Should fail
- Price < Cost: `price: 10, cost_price: 15` → ❌ Should fail

### 5.4 Exercise: Create a Reviews Feature

Now let's build a complete feature from scratch!

**Goal**: Add product reviews with ratings, text, and user information.

**Step 1: Create the Review Model**

**File: `backend/app/models/review.py`**

```python
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
```

**Step 2: Create Request/Response Schemas**

**File: `backend/app/schemas/review.py`**

```python
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
```

**Step 3: Create API Router**

**File: `backend/app/routers/reviews.py`**

```python
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
```

**Step 4: Register Everything**

**Update `backend/app/core/database.py`:**

```python
from app.models.product import Product
from app.models.order import Order
from app.models.customer import Customer
from app.models.review import Review  # ⬅️ Add this

# In init_beanie():
await init_beanie(
    database=cls.client[settings.DOCUMENTDB_DB_NAME],
    document_models=[
        Product,
        Order,
        Customer,
        Review,  # ⬅️ Add this
    ],
)
```

**Update `backend/app/main.py`:**

```python
from app.routers import products, customers, orders, admin, reviews  # ⬅️ Add reviews

app.include_router(reviews.router, prefix="/api/v1")  # ⬅️ Add this
```

**Step 5: Test Your New Feature!**

```powershell
# Restart the server
uvicorn app.main:app --reload
```

**Visit http://localhost:8000/docs and test:**

1. **Create a review:**
   ```json
   POST /api/v1/reviews
   {
     "product_id": "your-product-id-here",
     "customer_email": "test@example.com",
     "rating": 5,
     "title": "Amazing product!",
     "comment": "This product exceeded all my expectations. Highly recommended!"
   }
   ```

2. **List reviews for a product:**
   ```
   GET /api/v1/reviews?product_id=your-product-id&page=1&page_size=10
   ```

3. **Get review summary:**
   ```
   GET /api/v1/reviews/products/{product_id}/summary
   ```

4. **Mark review as helpful:**
   ```
   POST /api/v1/reviews/{review_id}/helpful
   ```

**✅ Congratulations!** You've built a complete feature with:
- ✅ Type-safe models with Beanie
- ✅ Validated request/response schemas with Pydantic
- ✅ Custom validators for business logic
- ✅ CRUD operations with FastAPI
- ✅ Aggregated statistics
- ✅ Automatic API documentation

---

## 🎯 Part 2 Complete!

**What you've accomplished:**
- ✅ Understood async/await patterns with database operations
- ✅ Built a benchmark suite to measure async performance
- ✅ Learned Pydantic + Beanie integration
- ✅ Created custom validators for business logic
- ✅ Built a complete Reviews feature from scratch

**What you've learned:**
- Why async matters (5-10x performance improvement!)
- FastAPI request lifecycle
- Separation of concerns (models vs schemas)
- Type safety throughout the stack
- Custom validation patterns

**Next Steps:**
Continue to [Part 3: DocumentDB Superpowers](FASTAPI_ADVANCED_WALKTHROUGH_PART3.md) to explore:
- Vector Search with HNSW/IVF indexing
- Geospatial Queries with PostGIS
- Advanced Aggregation Pipelines
