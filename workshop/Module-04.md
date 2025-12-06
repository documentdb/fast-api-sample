# Module 04 - Production Ready: Testing and Deployment

[< Advanced Querying and Filtering](Module-03.md) - [Home](Home.md)

---

## Introduction

In this final module, you'll learn how to make your Reviews API production-ready through comprehensive testing, documentation, and deployment best practices. You'll write unit and integration tests, optimize your API for performance, and prepare for deployment.

Testing is not optional for production applications - it's essential for maintaining code quality, preventing regressions, and enabling confident refactoring.

---

## Learning Objectives and Activities

- Write unit tests for API endpoints using pytest
- Create test fixtures for database testing
- Implement integration tests with async testing patterns
- Generate comprehensive API documentation
- Optimize Docker configuration for production
- Apply deployment best practices
- Implement health checks and monitoring

---

## Module Exercises

1. Activity 1: Set Up Testing Infrastructure
2. Activity 2: Write Unit Tests for Reviews API
3. Activity 3: Create Integration Tests
4. Activity 4: Enhance API Documentation
5. Activity 5: Production Optimization and Deployment

---

## Activity 1: Set Up Testing Infrastructure

Before writing tests, we need to set up the testing infrastructure with pytest and async support.

### Understanding the Test Setup

The starter application includes a basic test configuration in `backend/tests/conftest.py`. Let's understand and extend it.

1. **Examine `backend/tests/conftest.py`**:

   Key components:
   
   ```python
   import pytest
   from httpx import AsyncClient
   from beanie import init_beanie
   
   @pytest.fixture(scope="session")
   async def test_db():
       """Initialize test database."""
       # Uses separate test database
       test_db_name = "documentdb_test"
       # Initialize Beanie with test models
       await init_beanie(database=client[test_db_name], ...)
   
   @pytest.fixture
   async def client(test_db):
       """Create async HTTP client for testing."""
       async with AsyncClient(app=app, base_url="http://test") as ac:
           yield ac
   ```

### Create Test Fixtures for Reviews

1. **Add review fixtures to `backend/tests/conftest.py`**:

   Add these fixtures at the end of the file:
   
   ```python
   from app.models.review import Review
   
   
   @pytest.fixture
   async def sample_review(sample_product: Product, sample_customer: Customer) -> Review:
       """
       Create a sample review for testing.
       
       Automatically cleaned up after each test.
       """
       review = Review(
           customer_id=str(sample_customer.id),
           product_id=str(sample_product.id),
           customer_name=f"{sample_customer.first_name} {sample_customer.last_name}",
           product_name=sample_product.name,
           rating=5,
           title="Excellent product!",
           comment="This product exceeded all my expectations. Highly recommended!",
           verified_purchase=True,
           helpful_votes=10,
       )
       await review.insert()
       
       yield review
       
       # Cleanup
       await review.delete()
   
   
   @pytest.fixture
   async def multiple_reviews(sample_product: Product) -> list[Review]:
       """
       Create multiple reviews with varying ratings for testing.
       """
       # Create test customers
       customers = []
       for i in range(5):
           customer = Customer(
               email=f"test{i}@example.com",
               first_name=f"Test{i}",
               last_name="User",
               phone=f"+1-555-010{i}",
           )
           await customer.insert()
           customers.append(customer)
       
       # Create reviews with different ratings
       reviews = []
       ratings = [5, 4, 4, 3, 2]
       
       for i, rating in enumerate(ratings):
           review = Review(
               customer_id=str(customers[i].id),
               product_id=str(sample_product.id),
               customer_name=f"Test{i} User",
               product_name=sample_product.name,
               rating=rating,
               title=f"Review {i+1}",
               comment=f"This is test review number {i+1} with rating {rating}.",
               verified_purchase=i % 2 == 0,  # Alternate verified/unverified
               helpful_votes=i * 2,
           )
           await review.insert()
           reviews.append(review)
       
       yield reviews
       
       # Cleanup
       for review in reviews:
           await review.delete()
       for customer in customers:
           await customer.delete()
   ```

2. **Update imports in conftest.py**:

   Make sure Review is imported:
   
   ```python
   from app.models import Product, Customer, Order, Review
   
   # In init_beanie call:
   await init_beanie(
       database=client[test_db_name],
       document_models=[Product, Customer, Order, Review],  # Add Review
   )
   ```

---

## Activity 2: Write Unit Tests for Reviews API

Now let's create comprehensive tests for the Reviews API endpoints.

### Create the Test File

1. **Create `backend/tests/test_reviews.py`**:

   ```python
   """
   Tests for review endpoints.
   """
   
   import pytest
   from httpx import AsyncClient
   
   from app.models.review import Review
   from app.models.product import Product
   from app.models.customer import Customer
   
   
   @pytest.mark.asyncio
   class TestReviewEndpoints:
       """Test review API endpoints."""
       
       async def test_create_review(
           self, 
           client: AsyncClient,
           sample_product: Product,
           sample_customer: Customer
       ):
           """Test creating a new review."""
           review_data = {
               "product_id": str(sample_product.id),
               "customer_id": str(sample_customer.id),
               "rating": 5,
               "title": "Great product!",
               "comment": "This product is amazing. I love it and would recommend it to everyone!",
           }
           
           response = await client.post("/api/v1/reviews", json=review_data)
           
           assert response.status_code == 201
           data = response.json()
           assert data["rating"] == 5
           assert data["title"] == "Great product!"
           assert data["customer_name"] == f"{sample_customer.first_name} {sample_customer.last_name}"
           assert data["product_name"] == sample_product.name
           assert "_id" in data
       
       async def test_create_review_invalid_product(
           self,
           client: AsyncClient,
           sample_customer: Customer
       ):
           """Test that creating a review with invalid product ID fails."""
           review_data = {
               "product_id": "invalid_product_id_12345",
               "customer_id": str(sample_customer.id),
               "rating": 5,
               "title": "Great product!",
               "comment": "This should fail because product doesn't exist.",
           }
           
           response = await client.post("/api/v1/reviews", json=review_data)
           
           assert response.status_code == 404
           assert "not found" in response.json()["detail"].lower()
       
       async def test_create_duplicate_review(
           self,
           client: AsyncClient,
           sample_review: Review
       ):
           """Test that creating a duplicate review fails."""
           review_data = {
               "product_id": sample_review.product_id,
               "customer_id": sample_review.customer_id,
               "rating": 4,
               "title": "Another review",
               "comment": "This should fail because I already reviewed this product.",
           }
           
           response = await client.post("/api/v1/reviews", json=review_data)
           
           assert response.status_code == 409
           assert "already reviewed" in response.json()["detail"].lower()
       
       async def test_create_review_invalid_rating(
           self,
           client: AsyncClient,
           sample_product: Product,
           sample_customer: Customer
       ):
           """Test that invalid ratings are rejected."""
           review_data = {
               "product_id": str(sample_product.id),
               "customer_id": str(sample_customer.id),
               "rating": 6,  # Invalid: must be 1-5
               "title": "Test review",
               "comment": "This should fail due to invalid rating.",
           }
           
           response = await client.post("/api/v1/reviews", json=review_data)
           
           assert response.status_code == 422  # Validation error
       
       async def test_list_reviews(
           self,
           client: AsyncClient,
           sample_review: Review
       ):
           """Test listing reviews with pagination."""
           response = await client.get("/api/v1/reviews")
           
           assert response.status_code == 200
           data = response.json()
           assert "items" in data
           assert "total" in data
           assert data["total"] >= 1
           assert len(data["items"]) >= 1
       
       async def test_list_reviews_with_product_filter(
           self,
           client: AsyncClient,
           multiple_reviews: list[Review]
       ):
           """Test filtering reviews by product ID."""
           product_id = multiple_reviews[0].product_id
           
           response = await client.get(f"/api/v1/reviews?product_id={product_id}")
           
           assert response.status_code == 200
           data = response.json()
           assert data["total"] == 5  # We created 5 reviews
           assert all(item["product_id"] == product_id for item in data["items"])
       
       async def test_list_reviews_with_rating_filter(
           self,
           client: AsyncClient,
           multiple_reviews: list[Review]
       ):
           """Test filtering reviews by minimum rating."""
           response = await client.get("/api/v1/reviews?min_rating=4")
           
           assert response.status_code == 200
           data = response.json()
           # Should return reviews with rating >= 4
           assert all(item["rating"] >= 4 for item in data["items"])
       
       async def test_get_review(
           self,
           client: AsyncClient,
           sample_review: Review
       ):
           """Test getting a review by ID."""
           response = await client.get(f"/api/v1/reviews/{sample_review.id}")
           
           assert response.status_code == 200
           data = response.json()
           assert data["_id"] == str(sample_review.id)
           assert data["title"] == sample_review.title
       
       async def test_get_review_not_found(self, client: AsyncClient):
           """Test getting a non-existent review."""
           response = await client.get("/api/v1/reviews/507f1f77bcf86cd799439999")
           
           assert response.status_code == 404
       
       async def test_update_review(
           self,
           client: AsyncClient,
           sample_review: Review
       ):
           """Test updating a review."""
           update_data = {
               "rating": 4,
               "title": "Updated title",
               "comment": "I changed my mind. It's still good but not perfect.",
           }
           
           response = await client.put(
               f"/api/v1/reviews/{sample_review.id}",
               json=update_data
           )
           
           assert response.status_code == 200
           data = response.json()
           assert data["rating"] == 4
           assert data["title"] == "Updated title"
       
       async def test_delete_review(
           self,
           client: AsyncClient,
           sample_review: Review
       ):
           """Test deleting a review (soft delete)."""
           response = await client.delete(f"/api/v1/reviews/{sample_review.id}")
           
           assert response.status_code == 204
           
           # Verify it's soft deleted (is_active = False)
           deleted_review = await Review.get(sample_review.id)
           assert deleted_review is not None
           assert deleted_review.is_active is False
       
       async def test_mark_review_helpful(
           self,
           client: AsyncClient,
           sample_review: Review
       ):
           """Test marking a review as helpful."""
           initial_votes = sample_review.helpful_votes
           
           response = await client.post(f"/api/v1/reviews/{sample_review.id}/helpful")
           
           assert response.status_code == 200
           data = response.json()
           assert data["helpful_votes"] == initial_votes + 1
   ```

### Run the Tests

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install pytest dependencies** (if not already installed):
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

3. **Run all tests**:
   ```bash
   pytest -v
   ```

4. **Run only review tests**:
   ```bash
   pytest tests/test_reviews.py -v
   ```

5. **Run with coverage**:
   ```bash
   pytest --cov=app --cov-report=html
   ```

Expected output:
```
tests/test_reviews.py::TestReviewEndpoints::test_create_review PASSED
tests/test_reviews.py::TestReviewEndpoints::test_create_review_invalid_product PASSED
tests/test_reviews.py::TestReviewEndpoints::test_create_duplicate_review PASSED
...
======================== 12 passed in 2.34s ========================
```

---

## Activity 3: Create Integration Tests

Integration tests verify that different components work together correctly.

### Test Complex Workflows

1. **Add integration tests to `test_reviews.py`**:

   ```python
   @pytest.mark.asyncio
   class TestReviewIntegration:
       """Integration tests for review workflows."""
       
       async def test_complete_review_lifecycle(
           self,
           client: AsyncClient,
           sample_product: Product,
           sample_customer: Customer
       ):
           """Test the complete lifecycle of a review."""
           # 1. Create a review
           create_data = {
               "product_id": str(sample_product.id),
               "customer_id": str(sample_customer.id),
               "rating": 5,
               "title": "Lifecycle test",
               "comment": "Testing the complete review lifecycle from creation to deletion.",
           }
           
           create_response = await client.post("/api/v1/reviews", json=create_data)
           assert create_response.status_code == 201
           review_id = create_response.json()["_id"]
           
           # 2. Read the review
           get_response = await client.get(f"/api/v1/reviews/{review_id}")
           assert get_response.status_code == 200
           assert get_response.json()["title"] == "Lifecycle test"
           
           # 3. Mark as helpful
           helpful_response = await client.post(f"/api/v1/reviews/{review_id}/helpful")
           assert helpful_response.status_code == 200
           assert helpful_response.json()["helpful_votes"] == 1
           
           # 4. Update the review
           update_data = {
               "rating": 4,
               "title": "Updated lifecycle test",
           }
           update_response = await client.put(
               f"/api/v1/reviews/{review_id}",
               json=update_data
           )
           assert update_response.status_code == 200
           assert update_response.json()["rating"] == 4
           
           # 5. Delete the review
           delete_response = await client.delete(f"/api/v1/reviews/{review_id}")
           assert delete_response.status_code == 204
           
           # 6. Verify it's soft deleted
           deleted = await Review.get(review_id)
           assert deleted.is_active is False
       
       async def test_product_statistics_calculation(
           self,
           client: AsyncClient,
           multiple_reviews: list[Review]
       ):
           """Test that product statistics are calculated correctly."""
           product_id = multiple_reviews[0].product_id
           
           response = await client.get(
               f"/api/v1/reviews/products/{product_id}/statistics"
           )
           
           assert response.status_code == 200
           data = response.json()
           
           # Verify statistics
           assert data["total_reviews"] == 5
           assert data["average_rating"] == 3.6  # (5+4+4+3+2)/5
           
           # Verify rating distribution
           rating_dist = data["rating_distribution"]
           assert rating_dist["5"] == 1
           assert rating_dist["4"] == 2
           assert rating_dist["3"] == 1
           assert rating_dist["2"] == 1
           assert rating_dist["1"] == 0
       
       async def test_review_filtering_and_sorting(
           self,
           client: AsyncClient,
           multiple_reviews: list[Review]
       ):
           """Test complex filtering and sorting combinations."""
           product_id = multiple_reviews[0].product_id
           
           # Test 1: Get only high-rated reviews
           response = await client.get(
               f"/api/v1/reviews?product_id={product_id}&min_rating=4"
           )
           assert response.status_code == 200
           data = response.json()
           assert data["total"] == 3  # Two 4-star and one 5-star
           
           # Test 2: Sort by helpful votes descending
           response = await client.get(
               f"/api/v1/reviews?product_id={product_id}&sort_by=helpful_votes&sort_order=desc"
           )
           assert response.status_code == 200
           items = response.json()["items"]
           # Verify descending order
           for i in range(len(items) - 1):
               assert items[i]["helpful_votes"] >= items[i + 1]["helpful_votes"]
           
           # Test 3: Verified purchases only
           response = await client.get(
               f"/api/v1/reviews?product_id={product_id}&verified_only=true"
           )
           assert response.status_code == 200
           data = response.json()
           assert all(item["verified_purchase"] for item in data["items"])
   ```

### Run Integration Tests

```bash
pytest tests/test_reviews.py::TestReviewIntegration -v
```

---

## Activity 4: Enhance API Documentation

FastAPI automatically generates documentation, but we can enhance it significantly.

### Improve Endpoint Documentation

1. **Update router docstrings** with rich descriptions:

   ```python
   @router.post(
       "",
       response_model=ReviewResponse,
       status_code=status.HTTP_201_CREATED,
       summary="Create a new product review",
       description="""
       Create a new review for a product.
       
       ## Requirements
       - Customer must have an active account
       - Product must exist and be active
       - Customer can only review each product once
       
       ## Features
       - Automatic validation of rating (1-5 stars)
       - Denormalization of customer and product names for performance
       - Timestamp tracking for created and updated dates
       
       ## Common Errors
       - **404**: Product or customer not found
       - **409**: Customer already reviewed this product
       - **422**: Validation error (invalid rating, title too short, etc.)
       """,
       response_description="The created review with generated ID and timestamps",
       tags=["reviews"],
   )
   async def create_review(review_data: ReviewCreate) -> ReviewResponse:
       """Create a new product review."""
       # ... implementation
   ```

2. **Add response examples to schemas**:

   Update `backend/app/schemas/review.py`:
   
   ```python
   class ReviewResponse(BaseModel):
       """Review response schema."""
       
       id: str = Field(alias="_id")
       customer_id: str
       product_id: str
       customer_name: str
       product_name: str
       rating: int
       title: str
       comment: str
       helpful_votes: int
       verified_purchase: bool
       is_active: bool
       created_at: datetime
       updated_at: datetime
       
       class Config:
           populate_by_name = True
           json_schema_extra = {
               "example": {
                   "_id": "507f1f77bcf86cd799439011",
                   "customer_id": "507f1f77bcf86cd799439012",
                   "product_id": "507f1f77bcf86cd799439013",
                   "customer_name": "Alice Smith",
                   "product_name": "Wireless Headphones",
                   "rating": 5,
                   "title": "Excellent sound quality!",
                   "comment": "These headphones exceeded my expectations.",
                   "helpful_votes": 42,
                   "verified_purchase": True,
                   "is_active": True,
                   "created_at": "2025-12-01T10:30:00",
                   "updated_at": "2025-12-01T10:30:00"
               }
           }
   ```

3. **Add metadata to main app**:

   Update `backend/app/main.py`:
   
   ```python
   from fastapi import FastAPI
   
   app = FastAPI(
       title="E-commerce API",
       version="2.0.0",
       description="""
       ## E-commerce Platform API
       
       A comprehensive REST API for managing an e-commerce platform with:
       - Product catalog management
       - Customer accounts
       - Order processing
       - **Product reviews and ratings** (NEW!)
       
       ## Features
       - Async/await for high performance
       - MongoDB-compatible DocumentDB
       - Automatic data validation
       - Comprehensive error handling
       - Built-in API documentation
       
       ## Getting Started
       1. Browse the available endpoints below
       2. Try them out using the "Try it out" button
       3. View example requests and responses
       """,
       contact={
           "name": "API Support",
           "email": "support@example.com",
       },
       license_info={
           "name": "MIT",
       },
   )
   ```

4. **View the enhanced documentation**:

   - Open Swagger UI at `/docs`
   - Notice the improved descriptions and examples
   - Try the interactive documentation features

---

## Activity 5: Production Optimization and Deployment

Let's prepare the application for production deployment.

### Optimize Docker Configuration

1. **Create production Dockerfile** (`backend/Dockerfile.prod`):

   ```dockerfile
   FROM python:3.11-slim
   
   # Set working directory
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements
   COPY requirements.txt .
   
   # Install Python dependencies
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY ./app ./app
   
   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser
   
   # Expose port
   EXPOSE 8000
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
       CMD python -c "import requests; requests.get('http://localhost:8000/health')"
   
   # Run application
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Add health check endpoint** in `backend/app/main.py`:

   ```python
   from fastapi import FastAPI, status
   from fastapi.responses import JSONResponse
   
   @app.get("/health", tags=["health"])
   async def health_check():
       """
       Health check endpoint for monitoring and load balancers.
       
       Returns:
       - **status**: "healthy" if the API is running
       - **database**: "connected" if database is accessible
       """
       try:
           # Test database connection
           from app.core.database import client
           await client.admin.command('ping')
           db_status = "connected"
       except Exception:
           db_status = "disconnected"
       
       return JSONResponse(
           status_code=status.HTTP_200_OK,
           content={
               "status": "healthy",
               "database": db_status,
           }
       )
   ```

### Environment Configuration

1. **Create `.env.production` template**:

   ```env
   # Production Configuration
   DOCUMENTDB_URL=mongodb://username:password@your-documentdb-host:10260/?tls=true&tlsAllowInvalidCertificates=false
   DOCUMENTDB_DB_NAME=ecommerce_prod
   DEBUG=false
   RELOAD=false
   
   # Security
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   
   # Monitoring
   LOG_LEVEL=info
   ```

2. **Add environment validation** in `backend/app/core/config.py`:

   ```python
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       DOCUMENTDB_URL: str
       DOCUMENTDB_DB_NAME: str
       DEBUG: bool = False
       RELOAD: bool = False
       ALLOWED_ORIGINS: str = "*"
       LOG_LEVEL: str = "info"
       
       class Config:
           env_file = ".env"
           case_sensitive = True
       
       def validate_production(self):
           """Validate production configuration."""
           if not self.DEBUG:
               assert self.ALLOWED_ORIGINS != "*", "ALLOWED_ORIGINS must be specific in production"
               assert "password123" not in self.DOCUMENTDB_URL, "Change default password"
   
   settings = Settings()
   ```

### Performance Optimization

1. **Add connection pooling** in `backend/app/core/database.py`:

   ```python
   from motor.motor_asyncio import AsyncIOMotorClient
   
   # Connection pool settings for production
   client = AsyncIOMotorClient(
       settings.DOCUMENTDB_URL,
       maxPoolSize=50,  # Maximum connections
       minPoolSize=10,  # Minimum connections
       serverSelectionTimeoutMS=5000,
       connectTimeoutMS=10000,
   )
   ```

2. **Add caching for statistics** (optional):

   ```python
   from functools import lru_cache
   from datetime import datetime, timedelta
   
   # Simple in-memory cache
   _stats_cache = {}
   CACHE_TTL = timedelta(minutes=5)
   
   async def get_product_statistics_cached(product_id: str):
       """Get statistics with caching."""
       cache_key = f"stats_{product_id}"
       
       if cache_key in _stats_cache:
           cached_data, cached_time = _stats_cache[cache_key]
           if datetime.utcnow() - cached_time < CACHE_TTL:
               return cached_data
       
       # Calculate statistics
       stats = await get_product_statistics(product_id)
       
       # Cache result
       _stats_cache[cache_key] = (stats, datetime.utcnow())
       
       return stats
   ```

### Deployment Checklist

Before deploying to production:

- ✅ All tests pass (`pytest`)
- ✅ Environment variables configured for production
- ✅ Debug mode disabled (`DEBUG=false`)
- ✅ CORS origins restricted to your domain
- ✅ Database credentials changed from defaults
- ✅ Health check endpoint working
- ✅ Docker image builds successfully
- ✅ Connection pooling configured
- ✅ Logging configured appropriately
- ✅ API documentation reviewed and accurate

### Deployment Commands

1. **Build production image**:
   ```bash
   docker build -f Dockerfile.prod -t ecommerce-api:prod .
   ```

2. **Run production container**:
   ```bash
   docker run -d \
     --name ecommerce-api \
     --env-file .env.production \
     -p 8000:8000 \
     ecommerce-api:prod
   ```

3. **Verify health**:
   ```bash
   curl http://localhost:8000/health
   ```

---

## Validation Checklist

Your production setup is complete if:

- ✅ All unit tests pass
- ✅ Integration tests verify workflows
- ✅ Test coverage is > 80%
- ✅ API documentation is comprehensive
- ✅ Health check endpoint works
- ✅ Production Dockerfile created
- ✅ Environment configuration validated
- ✅ Connection pooling configured
- ✅ Security settings applied (CORS, passwords)
- ✅ Application runs in production mode

---

## Common Issues and Troubleshooting

### Issue 1: Tests failing with database connection errors

**Solution**:
- Ensure test database is separate from development database
- Check DocumentDB container is running during tests
- Verify test fixtures clean up properly

### Issue 2: Health check always returns unhealthy

**Solution**:
- Check database connection string is correct
- Verify DocumentDB is accessible from the container
- Check firewall rules and network configuration

### Issue 3: Production build fails

**Solution**:
- Verify all dependencies in `requirements.txt`
- Check Dockerfile paths are correct
- Ensure you have latest Python 3.11 base image

---

## Success Criteria

To complete this module successfully, you should be able to:

- ✅ Write comprehensive unit tests for all endpoints
- ✅ Create integration tests for complex workflows
- ✅ Use pytest fixtures effectively
- ✅ Generate test coverage reports
- ✅ Enhance API documentation with examples
- ✅ Create production-ready Docker configuration
- ✅ Implement health checks and monitoring
- ✅ Configure environment for production deployment
- ✅ Apply performance optimization techniques
- ✅ Follow deployment best practices

---

## Workshop Complete!

Congratulations! 🎉 You've completed the FastAPI + DocumentDB workshop.

### What You've Built

Throughout this workshop, you've created a production-ready Reviews API with:

1. **Module 01**: FastAPI fundamentals and routing
2. **Module 02**: Database integration with Beanie ODM
3. **Module 03**: Advanced querying and filtering
4. **Module 04**: Testing and deployment preparation

### Key Skills Acquired

- ✅ Building REST APIs with FastAPI
- ✅ Async Python programming
- ✅ DocumentDB/MongoDB integration
- ✅ Pydantic data validation
- ✅ Complex database queries and aggregations
- ✅ Comprehensive testing strategies
- ✅ Production deployment practices

### Next Steps

To continue learning:

1. **Deploy to Azure**:
   - Create Azure Cosmos DB for MongoDB account
   - Deploy to Azure App Service or Container Apps
   - Set up CI/CD with GitHub Actions

2. **Add Advanced Features**:
   - Image uploads for reviews
   - Review moderation workflow
   - Email notifications
   - Real-time analytics dashboard

3. **Explore Related Technologies**:
   - GraphQL with Strawberry
   - WebSocket support for real-time features
   - Background tasks with Celery
   - API rate limiting and authentication

### Resources

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Beanie ODM Docs](https://beanie-odm.dev/)
- [Azure Cosmos DB for MongoDB](https://learn.microsoft.com/azure/cosmos-db/mongodb/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Async/Await Tutorial](https://realpython.com/async-io-python/)

---

## Feedback

We'd love to hear your feedback on this workshop:

- What worked well?
- What could be improved?
- What topics would you like to see covered?

Thank you for participating! 🚀

[← Advanced Querying and Filtering](Module-03.md) | [Home](Home.md)
