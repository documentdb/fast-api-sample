# Module 01 - Foundation: Your First API Endpoint

[< Prerequisites and Setup](Module-00.md) - [Database Integration with Beanie ODM >](Module-02.md)

---

## Introduction

In this module, you'll build your first FastAPI endpoint from scratch and learn the core concepts of modern API development. You'll understand how FastAPI handles requests, validates data with Pydantic, and generates automatic documentation.

By the end of this module, you'll have created a working Reviews API endpoint that allows customers to submit product reviews - a feature you'll integrate with the existing e-commerce application.

---

## Learning Objectives and Activities

- Learn FastAPI fundamentals including routing and request handling
- Understand Pydantic schemas for data validation
- Create API endpoints with proper HTTP methods
- Test endpoints using Swagger UI
- Explore async/await patterns in Python
- Build a complete Reviews feature from scratch

---

## Module Exercises

1. Activity 1: Understanding FastAPI Routing
2. Activity 2: Create Pydantic Schemas for Reviews
3. Activity 3: Build Your First Endpoint
4. Activity 4: Add Full CRUD Operations
5. Activity 5: Test Your Work

---

## Activity 1: Understanding FastAPI Routing

Before we build our first endpoint, let's understand how FastAPI routes work and how they're organized in this application.

### FastAPI Basics

FastAPI is built on three core concepts:

1. **Path Operations** - Functions decorated with HTTP method decorators (`@app.get`, `@app.post`, etc.)
2. **Pydantic Models** - Python classes that define data structure and validation
3. **Dependency Injection** - Reusable components injected into route functions

### Exploring the Main Application

Let's examine how the application is structured:

1. **Open `backend/app/main.py`**

   Notice the key components:
   
   ```python
   from fastapi import FastAPI
   from app.routers import products, customers, orders
   
   app = FastAPI(
       title="E-commerce API",
       version="1.0.0",
       description="..."
   )
   
   # Include routers
   app.include_router(products.router)
   app.include_router(customers.router)
   app.include_router(orders.router)
   ```

2. **Understand the Router Pattern**:
   - Each domain (products, customers, orders) has its own router
   - Routers are defined in separate files under `app/routers/`
   - This keeps code organized and maintainable

3. **Open `backend/app/routers/products.py`**:

   Examine a simple GET endpoint:
   
   ```python
   @router.get("/products/{product_id}", response_model=ProductResponse)
   async def get_product(product_id: str):
       product = await Product.get(product_id)
       if not product:
           raise HTTPException(status_code=404, detail="Product not found")
       return product
   ```

   Key elements:
   - **Decorator**: `@router.get()` defines the HTTP method and path
   - **Path Parameter**: `{product_id}` extracts from URL
   - **Response Model**: Validates and documents the response
   - **Async Function**: Enables non-blocking database operations

### Project Structure for Routers

Each router follows this pattern:

```
backend/app/
├── routers/          # API endpoints
│   ├── __init__.py
│   ├── products.py   # Product endpoints
│   ├── customers.py  # Customer endpoints
│   └── orders.py     # Order endpoints
├── models/           # Database models (Beanie documents)
│   ├── product.py
│   ├── customer.py
│   └── order.py
└── schemas/          # Request/Response schemas (Pydantic)
    ├── product.py
    ├── customer.py
    └── order.py
```

**Why this separation?**
- **Models** represent data in the database
- **Schemas** represent data in API requests/responses
- **Routers** handle HTTP logic and orchestration

---

## Activity 2: Create Pydantic Schemas for Reviews

Now let's create the data schemas for our Reviews feature. We'll start by defining what data we need for product reviews.

### Create the Review Schema File

1. **Navigate to `backend/app/schemas/`**

2. **Create a new file** called `review.py`

3. **Add the following code**:

```python
"""
Review schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    
    product_id: str = Field(..., description="ID of the product being reviewed")
    customer_id: str = Field(..., description="ID of the customer submitting the review")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: str = Field(..., min_length=1, max_length=100, description="Review title")
    comment: str = Field(..., min_length=1, max_length=1000, description="Review text")
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        """Ensure rating is between 1 and 5."""
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewUpdate(BaseModel):
    """Schema for updating an existing review."""
    
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Review title")
    comment: Optional[str] = Field(None, min_length=1, max_length=1000, description="Review text")
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        """Ensure rating is between 1 and 5."""
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    """Schema for review responses."""
    
    id: str = Field(..., description="Unique review identifier")
    product_id: str
    customer_id: str
    rating: int
    title: str
    comment: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Understanding Pydantic Schemas

Let's break down what we just created:

1. **ReviewCreate** - Used for POST requests (creating reviews)
   - All fields are required (no `Optional`)
   - Includes validation rules (min/max length, rating range)
   - Custom validator ensures rating is 1-5

2. **ReviewUpdate** - Used for PATCH/PUT requests (updating reviews)
   - All fields are optional (allows partial updates)
   - Same validation rules apply when fields are provided

3. **ReviewResponse** - Used for responses (returning reviews)
   - Includes system fields like `id`, `created_at`, `updated_at`
   - `from_attributes = True` allows converting from database models

### Key Pydantic Features

- **Field()** - Defines field metadata and validation
  - `...` means required
  - `None` means optional
  - `ge=1, le=5` means "greater than or equal to 1, less than or equal to 5"
  - `min_length`, `max_length` for string validation

- **field_validator** - Custom validation logic
  - Runs after basic type validation
  - Can transform or reject values
  - Provides clear error messages

---

## Activity 3: Build Your First Endpoint

Now that we have our schemas, let's create the router with our first endpoint - getting all reviews for a product.

### Create the Review Router

1. **Navigate to `backend/app/routers/`**

2. **Create a new file** called `reviews.py`

3. **Add the base router setup**:

```python
"""
Review endpoints for the e-commerce API.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse

router = APIRouter(
    prefix="/api/v1/reviews",
    tags=["reviews"],
)


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: str,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
):
    """
    Get all reviews for a specific product.
    
    - **product_id**: The ID of the product
    - **skip**: Number of results to skip (for pagination)
    - **limit**: Maximum number of results to return
    """
    # TODO: Implement database query in next module
    # For now, return empty list
    return []
```

### Understanding the Endpoint

Let's break down this endpoint:

1. **Router Configuration**:
   - `prefix="/api/v1/reviews"` - All routes start with this path
   - `tags=["reviews"]` - Groups endpoints in Swagger UI

2. **Route Decorator**:
   - `@router.get()` - Handles HTTP GET requests
   - `"/product/{product_id}"` - URL pattern with path parameter
   - `response_model=List[ReviewResponse]` - Returns a list of reviews

3. **Function Parameters**:
   - `product_id: str` - Extracted from URL path
   - `skip: int = Query(...)` - Query parameter with default and validation
   - `limit: int = Query(...)` - Another query parameter

4. **Docstring**:
   - Appears in Swagger UI documentation
   - Describes parameters and behavior

### Register the Router

Now we need to add this router to the main application:

1. **Open `backend/app/main.py`**

2. **Add the import** at the top with the other router imports:

```python
from app.routers import products, customers, orders, reviews
```

3. **Include the router** with the other routers:

```python
app.include_router(reviews.router)
```

Your main.py should now have:

```python
# Include routers
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(reviews.router)  # New!
```

---

## Activity 4: Add Full CRUD Operations

Now let's add the remaining CRUD (Create, Read, Update, Delete) operations for reviews.

### Add Create Review Endpoint

In `backend/app/routers/reviews.py`, add this endpoint:

```python
@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate):
    """
    Create a new product review.
    
    - **product_id**: ID of the product being reviewed
    - **customer_id**: ID of the customer creating the review
    - **rating**: Rating from 1 to 5 stars
    - **title**: Brief review title
    - **comment**: Detailed review text
    """
    # TODO: Implement database insert in next module
    # For now, return a mock response
    from datetime import datetime
    return ReviewResponse(
        id="mock-id-123",
        product_id=review.product_id,
        customer_id=review.customer_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
```

### Add Get Single Review Endpoint

Add this endpoint to get a specific review by ID:

```python
@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    """
    Get a specific review by ID.
    
    - **review_id**: The unique identifier of the review
    """
    # TODO: Implement database query in next module
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found"
    )
```

### Add Update Review Endpoint

Add this endpoint to update an existing review:

```python
@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: str, review_update: ReviewUpdate):
    """
    Update an existing review.
    
    Only the fields provided will be updated.
    
    - **review_id**: The unique identifier of the review
    - **rating**: New rating (optional)
    - **title**: New title (optional)
    - **comment**: New comment (optional)
    """
    # TODO: Implement database update in next module
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found"
    )
```

### Add Delete Review Endpoint

Add this endpoint to delete a review:

```python
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: str):
    """
    Delete a review.
    
    - **review_id**: The unique identifier of the review to delete
    """
    # TODO: Implement database delete in next module
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found"
    )
```

### Add Customer Reviews Endpoint

Add this endpoint to get all reviews by a customer:

```python
@router.get("/customer/{customer_id}", response_model=List[ReviewResponse])
async def get_customer_reviews(
    customer_id: str,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
):
    """
    Get all reviews submitted by a specific customer.
    
    - **customer_id**: The ID of the customer
    - **skip**: Number of results to skip (for pagination)
    - **limit**: Maximum number of results to return
    """
    # TODO: Implement database query in next module
    return []
```

---

## Activity 5: Test Your Work

Now let's test the endpoints we've created using FastAPI's automatic Swagger UI.

### Start the Application

1. **Make sure your virtual environment is activated**:
   ```powershell
   cd backend
   .\.venv\Scripts\Activate.ps1
   ```

2. **Start the development server**:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The `--reload` flag enables hot-reloading during development.

### Test with Swagger UI

1. **Open the Swagger UI** in your browser:
   - Navigate to: http://localhost:8000/docs

2. **Locate the Reviews section**:
   - You should see a new section labeled "reviews"
   - Expand it to see all 6 endpoints we created

3. **Test the Create Review endpoint**:
   - Click on `POST /api/v1/reviews`
   - Click "Try it out"
   - Enter the following JSON in the request body:
     ```json
     {
       "product_id": "product-123",
       "customer_id": "customer-456",
       "rating": 5,
       "title": "Excellent product!",
       "comment": "This product exceeded my expectations. Highly recommended!"
     }
     ```
   - Click "Execute"
   - Check the response - you should see a 201 status code with the mock review data

4. **Test the Get Product Reviews endpoint**:
   - Click on `GET /api/v1/reviews/product/{product_id}`
   - Click "Try it out"
   - Enter a product ID: `product-123`
   - Adjust the pagination parameters if desired
   - Click "Execute"
   - You should see an empty array `[]` (we'll add data in the next module)

5. **Test the Get Review endpoint**:
   - Click on `GET /api/v1/reviews/{review_id}`
   - Click "Try it out"
   - Enter: `test-review-id`
   - Click "Execute"
   - You should see a 404 error (expected behavior for now)

6. **Test data validation**:
   - Go back to `POST /api/v1/reviews`
   - Try submitting invalid data:
     ```json
     {
       "product_id": "product-123",
       "customer_id": "customer-456",
       "rating": 10,
       "title": "",
       "comment": "Too short"
     }
     ```
   - Click "Execute"
   - You should see validation errors:
     - Rating must be ≤ 5
     - Title must have minimum length
     - Comment must have minimum length

### Understanding HTTP Status Codes

Notice the different status codes used:

- **200 OK** - Successful GET, PATCH requests
- **201 Created** - Successful POST (resource created)
- **204 No Content** - Successful DELETE
- **404 Not Found** - Resource doesn't exist
- **422 Unprocessable Entity** - Validation error

### Test with Alternative Methods

You can also test using curl or Python:

**Using curl**:
```powershell
curl -X POST "http://localhost:8000/api/v1/reviews" `
  -H "Content-Type: application/json" `
  -d '{
    "product_id": "product-123",
    "customer_id": "customer-456",
    "rating": 5,
    "title": "Great!",
    "comment": "Love this product"
  }'
```

**Using Python requests**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/reviews",
    json={
        "product_id": "product-123",
        "customer_id": "customer-456",
        "rating": 5,
        "title": "Great!",
        "comment": "Love this product"
    }
)
print(response.json())
```

---

## Validation Checklist

Your implementation is successful if:

- ✅ The application starts without errors
- ✅ Swagger UI shows the "reviews" section with 6 endpoints
- ✅ You can create a review (even though it returns mock data)
- ✅ Validation errors appear for invalid input (rating > 5, empty strings)
- ✅ GET endpoints return empty arrays or 404 errors as expected
- ✅ The API documentation is clear and descriptive

---

## Common Issues and Troubleshooting

### Issue 1: Import errors when starting the server

**Error**: `ModuleNotFoundError: No module named 'app.routers.reviews'`

**Solution**:
- Verify `reviews.py` is in the `backend/app/routers/` directory
- Make sure you imported it in `main.py`
- Restart the server with `--reload`

### Issue 2: Router not appearing in Swagger UI

**Error**: Reviews section doesn't show up

**Solution**:
- Check that you added `app.include_router(reviews.router)` in `main.py`
- Verify the router has the correct `prefix` and `tags`
- Hard refresh your browser (Ctrl+Shift+R)

### Issue 3: Validation not working

**Error**: Invalid data is accepted

**Solution**:
- Ensure you're using the correct schema (`ReviewCreate`, not `ReviewResponse`)
- Check that validators are defined with `@field_validator`
- Verify Field constraints (`ge`, `le`, `min_length`, etc.)

### Issue 4: Status codes are wrong

**Error**: Getting 200 instead of 201 for POST

**Solution**:
- Make sure you added `status_code=status.HTTP_201_CREATED` to the decorator
- Import `status` from `fastapi`

---

## Let's Review

Congratulations! You've created your first set of FastAPI endpoints!

### What You've Accomplished:

- ✅ Created Pydantic schemas for request/response validation
- ✅ Built a complete CRUD API with 6 endpoints
- ✅ Understood FastAPI routing and decorators
- ✅ Implemented proper HTTP methods and status codes
- ✅ Added automatic API documentation
- ✅ Tested endpoints with Swagger UI

### What You've Learned:

- **FastAPI Basics** - Routing, decorators, response models
- **Pydantic Validation** - Schemas, validators, field constraints
- **HTTP Methods** - GET, POST, PATCH, DELETE
- **Status Codes** - 200, 201, 204, 404, 422
- **API Documentation** - Automatic OpenAPI/Swagger generation
- **Query Parameters** - Pagination, filtering

### What's Next:

In the next module, we'll:
- Create the Review database model with Beanie
- Implement actual database operations
- Connect reviews to products and customers
- Add indexes for performance
- Handle database errors properly

---

## Module Solution

If you encountered issues, here's the complete code for this module:

<details>
<summary>Complete backend/app/schemas/review.py</summary>

```python
"""
Review schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    
    product_id: str = Field(..., description="ID of the product being reviewed")
    customer_id: str = Field(..., description="ID of the customer submitting the review")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: str = Field(..., min_length=1, max_length=100, description="Review title")
    comment: str = Field(..., min_length=1, max_length=1000, description="Review text")
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        """Ensure rating is between 1 and 5."""
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewUpdate(BaseModel):
    """Schema for updating an existing review."""
    
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Review title")
    comment: Optional[str] = Field(None, min_length=1, max_length=1000, description="Review text")
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        """Ensure rating is between 1 and 5."""
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    """Schema for review responses."""
    
    id: str = Field(..., description="Unique review identifier")
    product_id: str
    customer_id: str
    rating: int
    title: str
    comment: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```
</details>

<details>
<summary>Complete backend/app/routers/reviews.py</summary>

```python
"""
Review endpoints for the e-commerce API.
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse

router = APIRouter(
    prefix="/api/v1/reviews",
    tags=["reviews"],
)


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: str,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
):
    """
    Get all reviews for a specific product.
    
    - **product_id**: The ID of the product
    - **skip**: Number of results to skip (for pagination)
    - **limit**: Maximum number of results to return
    """
    return []


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate):
    """
    Create a new product review.
    
    - **product_id**: ID of the product being reviewed
    - **customer_id**: ID of the customer creating the review
    - **rating**: Rating from 1 to 5 stars
    - **title**: Brief review title
    - **comment**: Detailed review text
    """
    return ReviewResponse(
        id="mock-id-123",
        product_id=review.product_id,
        customer_id=review.customer_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    """
    Get a specific review by ID.
    
    - **review_id**: The unique identifier of the review
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found"
    )


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: str, review_update: ReviewUpdate):
    """
    Update an existing review.
    
    Only the fields provided will be updated.
    
    - **review_id**: The unique identifier of the review
    - **rating**: New rating (optional)
    - **title**: New title (optional)
    - **comment**: New comment (optional)
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found"
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: str):
    """
    Delete a review.
    
    - **review_id**: The unique identifier of the review to delete
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Review {review_id} not found"
    )


@router.get("/customer/{customer_id}", response_model=List[ReviewResponse])
async def get_customer_reviews(
    customer_id: str,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
):
    """
    Get all reviews submitted by a specific customer.
    
    - **customer_id**: The ID of the customer
    - **skip**: Number of results to skip (for pagination)
    - **limit**: Maximum number of results to return
    """
    return []
```
</details>

---

## Next Steps

Proceed to [Module 2: Database Integration with Beanie ODM](Module-02.md) to learn:

1. Creating Beanie document models
2. Implementing database operations (CRUD)
3. Adding indexes for performance
4. Handling database errors
5. Testing with real data
