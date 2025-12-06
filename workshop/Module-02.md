# Module 02 - Database Integration with Beanie ODM

[< Foundation: Your First API Endpoint](Module-01.md) - [Advanced Querying and Filtering >](Module-03.md)

---

## Introduction

In this module, you'll learn how to integrate your Reviews API with DocumentDB using Beanie ODM (Object Document Mapper). You'll transform the in-memory implementation from Module 01 into a fully persistent, database-backed API.

Beanie is an async ODM built on top of Pydantic and Motor, providing a pythonic way to interact with MongoDB-compatible databases like DocumentDB. It combines the power of async Python with automatic schema validation.

---

## Learning Objectives and Activities

- Understand Beanie ODM and its relationship to Pydantic
- Create Beanie document models with proper field types and validators
- Implement async CRUD operations with DocumentDB
- Add database indexes for query performance
- Handle database errors and edge cases
- Connect reviews to existing products and customers

---

## Module Exercises

1. Activity 1: Understanding Beanie Document Models
2. Activity 2: Create the Review Model
3. Activity 3: Update Router to Use Database
4. Activity 4: Add Indexes and Optimization
5. Activity 5: Test Database Integration

---

## Activity 1: Understanding Beanie Document Models

Before creating our Review model, let's understand how Beanie models work and how they differ from Pydantic schemas.

### Beanie vs Pydantic

**Pydantic Schemas** (what we used in Module 01):
- Define API request/response structure
- Validation only, no database interaction
- Located in `app/schemas/`

**Beanie Documents**:
- Represent actual database collections
- Include validation AND database operations
- Located in `app/models/`
- Inherit from `beanie.Document`

### Examining an Existing Model

1. **Open `backend/app/models/product.py`**:

   ```python
   from beanie import Document, Indexed
   from pydantic import Field
   
   class Product(Document):
       """Product document model."""
       
       name: Indexed(str)  # Creates an index on 'name'
       price: Decimal = Field(ge=0)
       sku: Indexed(str, unique=True)  # Unique index
       category: Indexed(str)
       stock_quantity: int = Field(ge=0, default=0)
       created_at: datetime = Field(default_factory=datetime.utcnow)
       
       class Settings:
           name = "products"  # Collection name in DocumentDB
           indexes = ["name", "sku", "category"]
   ```

   Key observations:
   - Inherits from `Document` (not `BaseModel`)
   - Uses `Indexed()` for fields that need database indexes
   - `Settings` class defines collection name and indexes
   - Field validators work exactly like Pydantic

2. **Database Operations with Beanie**:

   Common async operations:
   
   ```python
   # Create
   product = Product(name="Widget", price=9.99, sku="WDG-001")
   await product.insert()
   
   # Read
   product = await Product.get("document_id")
   products = await Product.find(Product.category == "Electronics").to_list()
   
   # Update
   product.price = 12.99
   await product.save()
   
   # Delete
   await product.delete()
   ```

### The Beanie + Pydantic Workflow

Here's how they work together:

1. **Request comes in** → Pydantic schema validates it (`ProductCreate`)
2. **Create Beanie document** → Convert to database model (`Product`)
3. **Save to database** → Beanie handles the interaction
4. **Return response** → Convert back to Pydantic schema (`ProductResponse`)

This separation keeps API contracts clean and database logic separate.

---

## Activity 2: Create the Review Model

Now let's create a Beanie document model for customer reviews.

### Design the Review Schema

Reviews should have:
- **Customer reference** - Who wrote the review
- **Product reference** - What product is being reviewed
- **Rating** - 1-5 stars
- **Title and comment** - Review content
- **Helpful votes** - Count of users who found it helpful
- **Verified purchase** - Did customer actually buy it
- **Timestamps** - Created and updated dates

### Create the Model File

1. **Create a new file** `backend/app/models/review.py`:

   ```python
   """
   Review model for DocumentDB.
   
   Represents customer product reviews.
   """
   
   from typing import Optional
   from datetime import datetime
   from beanie import Document, Indexed
   from pydantic import Field, field_validator
   
   
   class Review(Document):
       """Review document model."""
       
       # References
       customer_id: Indexed(str) = Field(description="Reference to Customer._id")
       product_id: Indexed(str) = Field(description="Reference to Product._id")
       
       # Denormalized data for faster queries
       customer_name: str = Field(description="Customer name for display")
       product_name: str = Field(description="Product name for display")
       
       # Review content
       rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
       title: str = Field(min_length=5, max_length=200)
       comment: str = Field(min_length=10, max_length=2000)
       
       # Metadata
       helpful_votes: int = Field(ge=0, default=0)
       verified_purchase: bool = Field(default=False)
       is_active: bool = Field(default=True, description="For moderation")
       
       # Timestamps
       created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
       updated_at: datetime = Field(default_factory=datetime.utcnow)
       
       @field_validator("title")
       @classmethod
       def validate_title(cls, v: str) -> str:
           """Ensure title is properly formatted."""
           return v.strip()
       
       @field_validator("comment")
       @classmethod
       def validate_comment(cls, v: str) -> str:
           """Ensure comment is properly formatted."""
           return v.strip()
       
       class Settings:
           name = "reviews"
           indexes = [
               "product_id",
               "customer_id",
               "rating",
               "created_at",
               [("product_id", 1), ("rating", -1)],  # Compound index
           ]
       
       class Config:
           json_schema_extra = {
               "example": {
                   "customer_id": "507f1f77bcf86cd799439011",
                   "product_id": "507f1f77bcf86cd799439012",
                   "customer_name": "Alice Smith",
                   "product_name": "Wireless Headphones",
                   "rating": 5,
                   "title": "Excellent sound quality!",
                   "comment": "These headphones exceeded my expectations. The noise cancellation is fantastic.",
                   "verified_purchase": True
               }
           }
   ```

2. **Update `backend/app/models/__init__.py`**:

   Add the Review model to the imports:
   
   ```python
   from app.models.product import Product
   from app.models.customer import Customer
   from app.models.order import Order
   from app.models.review import Review  # Add this line
   
   __all__ = ["Product", "Customer", "Order", "Review"]
   ```

### Understanding the Design Choices

**Denormalization**:
- We store `customer_name` and `product_name` directly
- This avoids joins when displaying reviews
- Trade-off: Slight data duplication for much faster reads

**Indexes**:
- `product_id` - Find all reviews for a product (most common query)
- `customer_id` - Find all reviews by a customer
- `rating` - Filter by star rating
- `created_at` - Sort by date
- Compound index on `(product_id, rating)` - Filter by product AND sort by rating

**Field Validation**:
- Rating constrained to 1-5
- Title and comment have length requirements
- Validators strip whitespace

---

## Activity 3: Update Router to Use Database

Now let's update the reviews router to use our Beanie model instead of the in-memory list.

### Update the Reviews Router

1. **Open `backend/app/routers/reviews.py`** and replace the entire content:

   ```python
   """
   Review API routes.
   """
   
   from typing import Optional
   from math import ceil
   from datetime import datetime
   from fastapi import APIRouter, HTTPException, Query, status
   
   from app.models.review import Review
   from app.models.product import Product
   from app.models.customer import Customer
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
       
       - **product_id**: ID of the product being reviewed
       - **customer_id**: ID of the customer writing the review
       - **rating**: Star rating from 1 to 5
       - **title**: Review title (5-200 characters)
       - **comment**: Review text (10-2000 characters)
       """
       # Verify product exists
       product = await Product.get(review_data.product_id)
       if not product or not product.is_active:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Active product with ID '{review_data.product_id}' not found",
           )
       
       # Verify customer exists
       customer = await Customer.get(review_data.customer_id)
       if not customer or not customer.is_active:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Active customer with ID '{review_data.customer_id}' not found",
           )
       
       # Check if customer already reviewed this product
       existing_review = await Review.find_one(
           Review.customer_id == review_data.customer_id,
           Review.product_id == review_data.product_id,
       )
       if existing_review:
           raise HTTPException(
               status_code=status.HTTP_409_CONFLICT,
               detail="You have already reviewed this product",
           )
       
       # Create review with denormalized data
       review = Review(
           **review_data.model_dump(),
           customer_name=f"{customer.first_name} {customer.last_name}",
           product_name=product.name,
       )
       await review.insert()
       
       return ReviewResponse(**review.model_dump())
   
   
   @router.get(
       "",
       response_model=ReviewListResponse,
       summary="List reviews with pagination and filtering",
   )
   async def list_reviews(
       page: int = Query(1, ge=1, description="Page number"),
       page_size: int = Query(20, ge=1, le=100, description="Items per page"),
       product_id: Optional[str] = Query(None, description="Filter by product ID"),
       customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
       min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating"),
   ) -> ReviewListResponse:
       """
       Retrieve a paginated list of reviews.
       
       Supports filtering by:
       - **product_id**: Get reviews for a specific product
       - **customer_id**: Get reviews by a specific customer
       - **min_rating**: Filter by minimum star rating
       """
       # Build query
       query = Review.find(Review.is_active == True)
       
       if product_id:
           query = query.find(Review.product_id == product_id)
       
       if customer_id:
           query = query.find(Review.customer_id == customer_id)
       
       if min_rating:
           query = query.find(Review.rating >= min_rating)
       
       # Get total count
       total = await query.count()
       
       # Calculate pagination
       pages = ceil(total / page_size) if total > 0 else 0
       skip = (page - 1) * page_size
       
       # Fetch paginated results (sort by created_at descending)
       reviews = await query.sort(-Review.created_at).skip(skip).limit(page_size).to_list()
       
       return ReviewListResponse(
           items=[ReviewResponse(**review.model_dump()) for review in reviews],
           total=total,
           page=page,
           page_size=page_size,
           pages=pages,
       )
   
   
   @router.get(
       "/{review_id}",
       response_model=ReviewResponse,
       summary="Get a review by ID",
   )
   async def get_review(review_id: str) -> ReviewResponse:
       """
       Retrieve a specific review by its ID.
       """
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
       """
       Update an existing review.
       
       Only the review author can update their review.
       """
       review = await Review.get(review_id)
       if not review:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Review with ID '{review_id}' not found",
           )
       
       # Update only provided fields
       update_data = review_data.model_dump(exclude_unset=True)
       if update_data:
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
       """
       Delete a review (soft delete by setting is_active to False).
       """
       review = await Review.get(review_id)
       if not review:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Review with ID '{review_id}' not found",
           )
       
       # Soft delete
       review.is_active = False
       review.updated_at = datetime.utcnow()
       await review.save()
   
   
   @router.post(
       "/{review_id}/helpful",
       response_model=ReviewResponse,
       summary="Mark review as helpful",
   )
   async def mark_helpful(review_id: str) -> ReviewResponse:
       """
       Increment the helpful votes counter for a review.
       """
       review = await Review.get(review_id)
       if not review:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Review with ID '{review_id}' not found",
           )
       
       review.helpful_votes += 1
       review.updated_at = datetime.utcnow()
       await review.save()
       
       return ReviewResponse(**review.model_dump())
   ```

2. **Register the router in `backend/app/main.py`**:

   Add the reviews router to the main application:
   
   ```python
   from app.routers import products, customers, orders, reviews
   
   # Include routers
   app.include_router(products.router, prefix="/api/v1")
   app.include_router(customers.router, prefix="/api/v1")
   app.include_router(orders.router, prefix="/api/v1")
   app.include_router(reviews.router, prefix="/api/v1")  # Add this line
   ```

3. **Update database initialization in `backend/app/core/database.py`**:

   Add Review to the document models:
   
   ```python
   from app.models import Product, Customer, Order, Review
   
   await init_beanie(
       database=client[settings.DOCUMENTDB_DB_NAME],
       document_models=[Product, Customer, Order, Review],  # Add Review
   )
   ```

### Key Implementation Details

**Validation Flow**:
1. Check if product exists and is active
2. Check if customer exists and is active
3. Prevent duplicate reviews from same customer on same product
4. Denormalize customer and product names for efficient display

**Query Building**:
- Use `Review.find()` to start a query
- Chain `.find()` calls to add filters
- Use `.sort()`, `.skip()`, and `.limit()` for pagination
- Call `.to_list()` or `.count()` to execute

**Error Handling**:
- 404 for missing products/customers/reviews
- 409 for duplicate reviews
- Proper status codes for all operations

---

## Activity 4: Add Indexes and Optimization

Database indexes are crucial for query performance. Let's understand and verify our indexing strategy.

### Understanding Index Usage

**When to Create Indexes**:
1. Fields used in `find()` queries
2. Fields used for sorting
3. Fields used frequently together (compound indexes)

**Index Trade-offs**:
- **Pros**: Faster reads, especially on large collections
- **Cons**: Slower writes, more storage space

### Verify Indexes in DocumentDB

1. **Open the DocumentDB VS Code extension**

2. **Navigate to your connection** → `ecommerce` → `reviews`

3. **Check indexes**:
   - Right-click on the `reviews` collection
   - Select **"View Indexes"** (if available)
   - Or use a query in the MongoDB shell:
   
   ```javascript
   db.reviews.getIndexes()
   ```

4. **Expected indexes**:
   - `_id` (automatic)
   - `product_id`
   - `customer_id`
   - `rating`
   - `created_at`
   - Compound: `{ product_id: 1, rating: -1 }`

### Query Performance Testing

Let's verify our indexes are being used:

1. **Create test data** using the API (via Swagger or the frontend)

2. **Run a query with explain**:

   In the DocumentDB extension, run:
   
   ```javascript
   db.reviews.find({ product_id: "your-product-id" }).explain("executionStats")
   ```

3. **Look for**:
   - `"stage": "IXSCAN"` - Index scan (good!)
   - `"stage": "COLLSCAN"` - Collection scan (slow on large data)

### Optimization Best Practices

1. **Denormalization** (already implemented):
   - Store `customer_name` and `product_name`
   - Avoids joining collections on every query
   - Perfect for read-heavy workloads

2. **Compound Indexes**:
   - `(product_id, rating)` supports queries like:
     - "All reviews for product X"
     - "All 5-star reviews for product X"
   
3. **Index Selectivity**:
   - `customer_id` - High selectivity (many unique values)
   - `rating` - Low selectivity (only 5 possible values)
   - Use high-selectivity fields first in compound indexes

---

## Activity 5: Test Database Integration

Let's verify everything works end-to-end.

### Manual Testing with Swagger UI

1. **Restart your application**:
   ```bash
   docker-compose restart backend
   ```

2. **Open Swagger UI**:
   - Go to the PORTS tab in Codespaces
   - Click the globe icon for port 8000
   - Navigate to `/docs`

3. **Test the review workflow**:

   **Step 1: Get a product ID**
   - Expand `GET /api/v1/products`
   - Click "Try it out"
   - Click "Execute"
   - Copy an `_id` from the response

   **Step 2: Get a customer ID**
   - Expand `GET /api/v1/customers`
   - Click "Try it out"
   - Click "Execute"
   - Copy an `_id` from the response

   **Step 3: Create a review**
   - Expand `POST /api/v1/reviews`
   - Click "Try it out"
   - Fill in the request body:
     ```json
     {
       "product_id": "paste-product-id-here",
       "customer_id": "paste-customer-id-here",
       "rating": 5,
       "title": "Excellent product!",
       "comment": "This product exceeded all my expectations. Highly recommended!"
     }
     ```
   - Click "Execute"
   - Verify you get a 201 response with the created review

   **Step 4: List reviews for the product**
   - Expand `GET /api/v1/reviews`
   - Click "Try it out"
   - Enter the `product_id` in the filter
   - Click "Execute"
   - Verify your review appears

   **Step 5: Test duplicate prevention**
   - Try creating the same review again
   - Verify you get a 409 Conflict error

   **Step 6: Mark as helpful**
   - Copy the review `_id`
   - Expand `POST /api/v1/reviews/{review_id}/helpful`
   - Paste the review ID
   - Click "Execute"
   - Verify `helpful_votes` incremented

### Verify in DocumentDB Extension

1. **Open the DocumentDB extension**

2. **Navigate to** `ecommerce` → `reviews`

3. **View your review**:
   - Expand the collection to see documents
   - Click on your review to view its full content
   - Verify all fields are present and correct

4. **Check the denormalized data**:
   - Confirm `customer_name` and `product_name` are populated
   - These should match the actual customer and product data

### Test Error Scenarios

1. **Invalid product ID**:
   ```json
   {
     "product_id": "invalid-id-12345",
     "customer_id": "valid-customer-id",
     "rating": 5,
     "title": "Test",
     "comment": "This should fail"
   }
   ```
   Expected: 404 Not Found

2. **Rating out of range**:
   ```json
   {
     "product_id": "valid-product-id",
     "customer_id": "valid-customer-id",
     "rating": 6,
     "title": "Test",
     "comment": "Rating too high"
   }
   ```
   Expected: 422 Validation Error

3. **Title too short**:
   ```json
   {
     "product_id": "valid-product-id",
     "customer_id": "valid-customer-id",
     "rating": 5,
     "title": "Bad",
     "comment": "Title is too short"
   }
   ```
   Expected: 422 Validation Error

---

## Validation Checklist

Your database integration is successful if:

- ✅ Review model created in `backend/app/models/review.py`
- ✅ Model registered in `__init__.py` and `database.py`
- ✅ Router updated to use Beanie operations
- ✅ Reviews router registered in `main.py`
- ✅ Can create reviews via Swagger UI
- ✅ Reviews appear in DocumentDB extension
- ✅ Duplicate reviews are prevented (409 error)
- ✅ Invalid IDs return 404 errors
- ✅ Validation errors return 422 errors
- ✅ Denormalized fields are populated correctly
- ✅ Indexes are created in DocumentDB

---

## Common Issues and Troubleshooting

### Issue 1: "Review model not found" error

**Solution**:
- Verify `Review` is imported in `backend/app/models/__init__.py`
- Verify `Review` is included in `init_beanie()` call
- Restart the backend service: `docker-compose restart backend`

### Issue 2: Duplicate reviews not prevented

**Solution**:
- Check the duplicate check logic in `create_review()`
- Verify you're using the correct customer_id and product_id
- Ensure both IDs match exactly

### Issue 3: Indexes not created

**Solution**:
- Indexes are created automatically when Beanie initializes
- Restart the application to trigger index creation
- Manually create indexes using DocumentDB extension if needed

### Issue 4: Denormalized fields are empty

**Solution**:
- Verify product and customer exist before creating review
- Check that `customer.first_name`, `customer.last_name`, and `product.name` are populated
- Ensure the denormalization logic executes before `insert()`

---

## Success Criteria

To complete this module successfully, you should be able to:

- ✅ Understand the difference between Beanie models and Pydantic schemas
- ✅ Create a Beanie document model with proper validation
- ✅ Implement async CRUD operations with DocumentDB
- ✅ Use indexes to optimize query performance
- ✅ Handle database errors gracefully
- ✅ Test your API with real database interactions
- ✅ Verify data persistence in DocumentDB

---

## Next Steps

Proceed to [Module 3: Advanced Querying and Filtering](Module-03.md) to learn:

1. Complex aggregation queries
2. Full-text search implementation
3. Advanced filtering patterns
4. Query optimization techniques
5. Calculating average ratings and statistics

---

## Resources

- [Beanie Documentation](https://beanie-odm.dev/)
- [Beanie Query Operators](https://beanie-odm.dev/tutorial/find-query/)
- [MongoDB Indexes](https://www.mongodb.com/docs/manual/indexes/)
- [Motor Async Driver](https://motor.readthedocs.io/)
- [Async Python Patterns](https://docs.python.org/3/library/asyncio.html)
