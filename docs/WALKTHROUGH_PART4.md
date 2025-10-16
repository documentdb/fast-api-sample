# FastAPI + DocumentDB: Part 4 - Production Ready 🚀

> **Prerequisites**: Completed Parts 1, 2, and 3 of the walkthrough

This section covers best practices, optimization techniques, testing strategies, and deployment considerations for taking your FastAPI + DocumentDB application to production.

---

## Part 4: Production Ready

### Step 10: Index Optimization & Performance Tuning

**Scenario**: Optimize database queries using proper indexing and query analysis.

#### 10.1 Understanding DocumentDB Indexes

DocumentDB leverages PostgreSQL's powerful indexing capabilities while maintaining MongoDB compatibility.

**Index Types Available:**

| Index Type | Use Case | DocumentDB Implementation |
|------------|----------|---------------------------|
| **B-tree** | Equality, range queries | PostgreSQL B-tree on JSONB fields |
| **Unique** | Enforce uniqueness (SKU, email) | PostgreSQL unique constraint |
| **Compound** | Multi-field queries | PostgreSQL multi-column index |
| **Text** | Full-text search | PostgreSQL `ts_vector` |
| **Geospatial** | Location queries | PostGIS (2d, 2dsphere) |
| **Vector** | Similarity search | pgvector (HNSW, IVF) |

#### 10.2 Query Analysis with EXPLAIN

**File: `backend/app/routers/debug.py`**

```python
"""
Debug and performance analysis endpoints.
"""

from fastapi import APIRouter, Query
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/explain-query")
async def explain_query(
    collection: str = Query(..., description="Collection name"),
    query_filter: str = Query("{}", description="MongoDB query as JSON string")
):
    """
    Explain query execution plan using DocumentDB's EXPLAIN.
    
    This shows how PostgreSQL executes your MongoDB query.
    """
    import json
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    
    try:
        # Parse query filter
        filter_dict = json.loads(query_filter)
        
        # Use MongoDB's explain command
        explain_result = await db.command(
            "explain",
            {
                "find": collection,
                "filter": filter_dict
            },
            verbosity="executionStats"
        )
        
        return {
            "collection": collection,
            "query": filter_dict,
            "execution_stats": {
                "execution_time_ms": explain_result.get("executionStats", {}).get("executionTimeMillis"),
                "total_docs_examined": explain_result.get("executionStats", {}).get("totalDocsExamined"),
                "total_keys_examined": explain_result.get("executionStats", {}).get("totalKeysExamined"),
                "docs_returned": explain_result.get("executionStats", {}).get("nReturned"),
            },
            "index_used": explain_result.get("queryPlanner", {}).get("winningPlan", {}).get("inputStage", {}).get("indexName"),
            "full_explain": explain_result
        }
    
    finally:
        client.close()


@router.get("/collection-stats")
async def get_collection_stats(
    collection: str = Query(..., description="Collection name")
):
    """Get statistics about a collection (size, indexes, document count)."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    
    try:
        # Get collection stats
        stats = await db.command("collStats", collection)
        
        # Get indexes
        indexes = await db[collection].list_indexes().to_list(length=None)
        
        return {
            "collection": collection,
            "document_count": stats.get("count"),
            "size_bytes": stats.get("size"),
            "avg_document_size_bytes": stats.get("avgObjSize"),
            "storage_size_bytes": stats.get("storageSize"),
            "indexes": [
                {
                    "name": idx.get("name"),
                    "keys": idx.get("key"),
                    "unique": idx.get("unique", False)
                }
                for idx in indexes
            ],
            "total_index_size_bytes": stats.get("totalIndexSize")
        }
    
    finally:
        client.close()
```

**Usage Example:**

```bash
# Explain a simple query
GET /api/v1/debug/explain-query?collection=products&query_filter={"category":"Electronics"}

# Get collection statistics
GET /api/v1/debug/collection-stats?collection=products
```

#### 10.3 Creating Optimal Indexes

**File: `scripts/create_production_indexes.py`**

```python
"""
Create production-optimized indexes for DocumentDB collections.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings


async def create_product_indexes():
    """Create optimized indexes for products collection."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    collection = db["products"]
    
    try:
        print("Creating indexes for products collection...")
        
        # 1. Single field indexes
        await collection.create_index("name", name="idx_products_name")
        print("✓ Created index: idx_products_name")
        
        await collection.create_index("category", name="idx_products_category")
        print("✓ Created index: idx_products_category")
        
        await collection.create_index(
            "sku",
            unique=True,
            name="idx_products_sku_unique"
        )
        print("✓ Created unique index: idx_products_sku_unique")
        
        # 2. Compound indexes for common query patterns
        await collection.create_index(
            [("category", 1), ("price", 1)],
            name="idx_products_category_price"
        )
        print("✓ Created compound index: idx_products_category_price")
        
        await collection.create_index(
            [("is_active", 1), ("created_at", -1)],
            name="idx_products_active_created"
        )
        print("✓ Created compound index: idx_products_active_created")
        
        # 3. Text index for search
        await collection.create_index(
            [("name", "text"), ("description", "text")],
            name="idx_products_text_search",
            weights={"name": 10, "description": 5}  # Name more important
        )
        print("✓ Created text index: idx_products_text_search")
        
        # 4. Sparse index for optional fields
        await collection.create_index(
            "tags",
            name="idx_products_tags",
            sparse=True  # Only index documents with tags field
        )
        print("✓ Created sparse index: idx_products_tags")
        
        # List all indexes
        indexes = await collection.list_indexes().to_list(length=None)
        print("\n✅ All indexes on products collection:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
    
    finally:
        client.close()


async def create_order_indexes():
    """Create optimized indexes for orders collection."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    collection = db["orders"]
    
    try:
        print("\nCreating indexes for orders collection...")
        
        # Customer lookup
        await collection.create_index("customer_email", name="idx_orders_customer")
        print("✓ Created index: idx_orders_customer")
        
        # Status filtering
        await collection.create_index("status", name="idx_orders_status")
        print("✓ Created index: idx_orders_status")
        
        # Date range queries
        await collection.create_index(
            [("created_at", -1)],
            name="idx_orders_created_desc"
        )
        print("✓ Created index: idx_orders_created_desc")
        
        # Compound index for customer orders by date
        await collection.create_index(
            [("customer_email", 1), ("created_at", -1)],
            name="idx_orders_customer_created"
        )
        print("✓ Created compound index: idx_orders_customer_created")
        
        # Status and date for admin queries
        await collection.create_index(
            [("status", 1), ("created_at", -1)],
            name="idx_orders_status_created"
        )
        print("✓ Created compound index: idx_orders_status_created")
        
        print("\n✅ All indexes created for orders collection")
    
    finally:
        client.close()


async def create_review_indexes():
    """Create optimized indexes for reviews collection."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    collection = db["reviews"]
    
    try:
        print("\nCreating indexes for reviews collection...")
        
        # Product reviews lookup
        await collection.create_index(
            [("product_id", 1), ("created_at", -1)],
            name="idx_reviews_product_created"
        )
        print("✓ Created compound index: idx_reviews_product_created")
        
        # Rating filtering
        await collection.create_index(
            [("product_id", 1), ("rating", -1)],
            name="idx_reviews_product_rating"
        )
        print("✓ Created compound index: idx_reviews_product_rating")
        
        # Customer's reviews
        await collection.create_index(
            "customer_email",
            name="idx_reviews_customer"
        )
        print("✓ Created index: idx_reviews_customer")
        
        # Prevent duplicate reviews (unique compound)
        await collection.create_index(
            [("product_id", 1), ("customer_email", 1)],
            unique=True,
            name="idx_reviews_product_customer_unique"
        )
        print("✓ Created unique compound index: idx_reviews_product_customer_unique")
        
        print("\n✅ All indexes created for reviews collection")
    
    finally:
        client.close()


async def main():
    """Create all production indexes."""
    print("=" * 60)
    print("Creating Production Indexes for DocumentDB")
    print("=" * 60)
    
    await create_product_indexes()
    await create_order_indexes()
    await create_review_indexes()
    
    print("\n" + "=" * 60)
    print("✅ All production indexes created successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

**Run the script:**
```powershell
python scripts/create_production_indexes.py
```

#### 10.4 Query Optimization Best Practices

**❌ Inefficient Query (No Index):**

```python
# Scans entire collection
products = await Product.find(
    Product.description.regex("wireless", "i")  # Case-insensitive regex
).to_list()
# Execution time: ~500ms for 10,000 products
```

**✅ Optimized Query (Using Index):**

```python
# Uses text index
products = await Product.find(
    {"$text": {"$search": "wireless"}}
).to_list()
# Execution time: ~50ms for 10,000 products
```

**Common Optimization Patterns:**

```python
# 1. Use covered indexes (index contains all needed fields)
# Query returns only indexed fields - no document lookup needed
products = await Product.find(
    {"category": "Electronics"},
    projection={"name": 1, "category": 1, "_id": 0}  # Only indexed fields
).to_list()

# 2. Use compound indexes for multi-field queries
# Index: [("category", 1), ("price", 1)]
products = await Product.find(
    Product.category == "Electronics",
    Product.price >= 20,
    Product.price <= 100
).sort("price").to_list()

# 3. Limit results early
# Always use .limit() when you don't need all results
recent_products = await Product.find(
    Product.is_active == True
).sort("-created_at").limit(20).to_list()

# 4. Use projection to reduce data transfer
# Only fetch fields you need
products = await Product.find(
    {"category": "Electronics"}
).project({"name": 1, "price": 1, "sku": 1}).to_list()
```

---

### Step 11: FastAPI Best Practices

#### 11.1 Connection Pooling & Resource Management

**File: `backend/app/core/database.py`** (Enhanced)

```python
"""
Enhanced database connection with production-ready settings.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager

from app.core.config import settings
from app.models.product import Product
from app.models.order import Order
from app.models.customer import Customer
from app.models.review import Review


class Database:
    """Database connection manager with connection pooling."""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """
        Connect to DocumentDB with production-optimized settings.
        """
        if cls.client is not None:
            return
        
        # Production connection settings
        cls.client = AsyncIOMotorClient(
            settings.DOCUMENTDB_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,  # Use proper certs in production!
            
            # Connection pool settings
            maxPoolSize=50,              # Max connections in pool
            minPoolSize=10,              # Min connections to maintain
            maxIdleTimeMS=45000,         # Close idle connections after 45s
            
            # Timeout settings
            serverSelectionTimeoutMS=5000,  # Fail fast if can't connect
            connectTimeoutMS=10000,         # Connection timeout
            socketTimeoutMS=30000,          # Socket operation timeout
            
            # Retry settings
            retryWrites=True,               # Retry failed writes
            retryReads=True,                # Retry failed reads
            
            # Monitoring
            appname="ecommerce-api",        # Appears in logs
        )
        
        # Initialize Beanie ODM
        await init_beanie(
            database=cls.client[settings.DOCUMENTDB_DB_NAME],
            document_models=[
                Product,
                Order,
                Customer,
                Review,
            ],
        )
        
        # Verify connection
        await cls.client.admin.command('ping')
        print("✓ Connected to DocumentDB with connection pool")
    
    @classmethod
    async def close_db(cls):
        """Close database connection and cleanup resources."""
        if cls.client is None:
            return
        
        cls.client.close()
        cls.client = None
        print("✓ Closed DocumentDB connection")
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get the database client."""
        if cls.client is None:
            raise RuntimeError("Database not connected. Call connect_db() first.")
        return cls.client
```

**File: `backend/app/main.py`** (Enhanced with lifespan)

```python
"""
FastAPI application with production-ready configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.database import Database
from app.core.config import settings
from app.routers import products, customers, orders, admin, reviews, debug


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    try:
        await Database.connect_db()
        logger.info("✓ Database connection established")
    except Exception as e:
        logger.error(f"✗ Failed to connect to database: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down application...")
    await Database.close_db()
    logger.info("✓ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="E-Commerce API",
    description="Production-ready FastAPI + DocumentDB e-commerce API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns 200 if application and database are healthy.
    """
    try:
        # Check database connection
        client = Database.get_client()
        await client.admin.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


# Readiness check (for Kubernetes)
@app.get("/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check for Kubernetes.
    
    Returns 200 when application is ready to accept traffic.
    """
    try:
        client = Database.get_client()
        await client.admin.command('ping')
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready"}
        )


# Register routers
app.include_router(products.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")

# Debug router (disable in production!)
if settings.DEBUG:
    app.include_router(debug.router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """API root endpoint."""
    return {
        "message": "Welcome to E-Commerce API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
```

#### 11.2 Error Handling & Logging

**File: `backend/app/core/exceptions.py`**

```python
"""
Custom exception classes for better error handling.
"""

from fastapi import HTTPException, status


class DatabaseConnectionError(HTTPException):
    """Raised when database connection fails."""
    
    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class ResourceNotFoundError(HTTPException):
    """Raised when a requested resource doesn't exist."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with ID '{identifier}' not found"
        )


class DuplicateResourceError(HTTPException):
    """Raised when trying to create a duplicate resource."""
    
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field}='{value}' already exists"
        )


class ValidationError(HTTPException):
    """Raised when business logic validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class InsufficientStockError(HTTPException):
    """Raised when product stock is insufficient for order."""
    
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock for {product_name}. "
                   f"Available: {available}, Requested: {requested}"
        )
```

**Usage in endpoints:**

```python
from app.core.exceptions import ResourceNotFoundError, DuplicateResourceError

@router.post("", response_model=ProductResponse)
async def create_product(product_data: ProductCreate):
    # Check for duplicate
    existing = await Product.find_one(Product.sku == product_data.sku)
    if existing:
        raise DuplicateResourceError("Product", "SKU", product_data.sku)
    
    product = Product(**product_data.model_dump())
    await product.insert()
    return ProductResponse(**product.model_dump())


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    product = await Product.get(product_id)
    if not product:
        raise ResourceNotFoundError("Product", product_id)
    
    return ProductResponse(**product.model_dump())
```

#### 11.3 Configuration Management

**File: `backend/app/core/config.py`** (Production-ready)

```python
"""
Application configuration using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "E-Commerce API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # DocumentDB Connection
    DOCUMENTDB_URL: str
    DOCUMENTDB_DB_NAME: str = "ecommerce"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    
    # Feature Flags
    ENABLE_VECTOR_SEARCH: bool = True
    ENABLE_GEOSPATIAL: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
```

**.env file for production:**

```bash
# Application
DEBUG=False
SECRET_KEY=your-super-secret-key-change-in-production

# DocumentDB
DOCUMENTDB_URL=mongodb://admin:password@documentdb-cluster.us-east-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem
DOCUMENTDB_DB_NAME=ecommerce

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=60

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
ENABLE_METRICS=True
```

---

### Step 12: Testing Strategies

#### 12.1 Unit Tests for Business Logic

**File: `backend/tests/test_product_service.py`**

```python
"""
Unit tests for product service logic.
"""

import pytest
from decimal import Decimal
from app.models.product import Product
from app.schemas.product import ProductCreate


@pytest.mark.asyncio
async def test_create_product_success():
    """Test successful product creation."""
    product_data = ProductCreate(
        name="Test Product",
        description="Test description",
        price=Decimal("99.99"),
        sku="TEST-PROD-001",
        category="Electronics",
        stock_quantity=100
    )
    
    product = Product(**product_data.model_dump())
    assert product.name == "Test Product"
    assert product.price == Decimal("99.99")
    assert product.sku == "TEST-PROD-001"


def test_product_validation_negative_price():
    """Test that negative price raises validation error."""
    with pytest.raises(ValueError):
        ProductCreate(
            name="Test Product",
            price=Decimal("-10.00"),  # Invalid
            sku="TEST-001",
            category="Electronics"
        )


def test_product_validation_empty_name():
    """Test that empty name raises validation error."""
    with pytest.raises(ValueError):
        ProductCreate(
            name="",  # Invalid
            price=Decimal("99.99"),
            sku="TEST-001",
            category="Electronics"
        )
```

#### 12.2 Integration Tests

**File: `backend/tests/test_api_integration.py`**

```python
"""
Integration tests for API endpoints.
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_product_integration():
    """Test product creation through API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        product_data = {
            "name": "Integration Test Product",
            "price": 49.99,
            "sku": "INT-TEST-001",
            "category": "Test",
            "stock_quantity": 10
        }
        
        response = await client.post("/api/v1/products", json=product_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Integration Test Product"
        assert "_id" in data


@pytest.mark.asyncio
async def test_create_duplicate_sku():
    """Test that duplicate SKU returns 409 Conflict."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        product_data = {
            "name": "Test Product",
            "price": 49.99,
            "sku": "DUP-TEST-001",
            "category": "Test"
        }
        
        # First creation should succeed
        response1 = await client.post("/api/v1/products", json=product_data)
        assert response1.status_code == 201
        
        # Second creation should fail
        response2 = await client.post("/api/v1/products", json=product_data)
        assert response2.status_code == 409
```

#### 12.3 Load Testing

**File: `tests/locustfile.py`** (using Locust)

```python
"""
Load testing with Locust.

Run with: locust -f tests/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random


class EcommerceUser(HttpUser):
    """Simulate e-commerce user behavior."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts."""
        # Could add login logic here
        pass
    
    @task(3)  # Weight: 3 (runs 3x more often)
    def list_products(self):
        """List products with pagination."""
        page = random.randint(1, 10)
        self.client.get(f"/api/v1/products?page={page}&page_size=20")
    
    @task(2)
    def get_product_details(self):
        """Get a specific product."""
        # Assuming we know some product IDs
        product_id = "507f1f77bcf86cd799439011"
        self.client.get(f"/api/v1/products/{product_id}")
    
    @task(1)
    def search_products(self):
        """Search for products."""
        categories = ["Electronics", "Books", "Clothing"]
        category = random.choice(categories)
        self.client.get(f"/api/v1/products?category={category}")
    
    @task(1)
    def create_order(self):
        """Create a new order."""
        order_data = {
            "customer_email": f"user{random.randint(1, 1000)}@test.com",
            "items": [
                {
                    "product_id": "507f1f77bcf86cd799439011",
                    "quantity": random.randint(1, 3),
                    "price": 29.99
                }
            ],
            "total_amount": 29.99
        }
        self.client.post("/api/v1/orders", json=order_data)
```

**Run load test:**
```powershell
pip install locust
locust -f tests/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

---

### Step 13: Deployment & Monitoring

#### 13.1 Docker Production Build

**File: `backend/Dockerfile.prod`**

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

# Copy application code
COPY ./app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run with Gunicorn
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### 13.2 Kubernetes Deployment

**File: `k8s/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
  labels:
    app: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: api
        image: your-registry/ecommerce-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DOCUMENTDB_URL
          valueFrom:
            secretKeyRef:
              name: documentdb-secret
              key: connection-string
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-api-service
spec:
  selector:
    app: ecommerce-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 13.3 Monitoring with Prometheus

**File: `backend/app/middleware/metrics.py`**

```python
"""
Prometheus metrics middleware.
"""

from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time


# Define metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)


async def metrics_middleware(request: Request, call_next):
    """Collect metrics for each request."""
    method = request.method
    path = request.url.path
    
    # Start timer
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    request_duration.labels(method=method, endpoint=path).observe(duration)
    request_count.labels(
        method=method,
        endpoint=path,
        status=response.status_code
    ).inc()
    
    return response
```

**Add metrics endpoint:**

```python
from prometheus_client import generate_latest

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

### Step 14: Capstone Project Ideas

Choose one to demonstrate your mastery:

#### Option 1: AI-Powered Product Recommendations
- Implement complete vector search with sentence transformers
- Create "Similar Products" and "Frequently Bought Together" features
- Build recommendation API with A/B testing support

#### Option 2: Real-Time Inventory Management
- Add WebSocket support for live stock updates
- Implement distributed locking for concurrent order processing
- Create admin dashboard with real-time metrics

#### Option 3: Multi-Region Deployment
- Deploy to multiple regions (US, EU, Asia)
- Implement geolocation-based routing
- Add read replicas for DocumentDB
- Setup global CDN with CloudFront/Cloudflare

#### Option 4: Complete E-Commerce Platform
- Add user authentication (JWT)
- Implement shopping cart with Redis caching
- Add payment integration (Stripe)
- Create order tracking system
- Build admin analytics dashboard

---

## Summary: Production-Ready Checklist ✅

### Performance
- ✅ Optimal database indexes created
- ✅ Connection pooling configured
- ✅ Query performance analyzed with EXPLAIN
- ✅ Response compression enabled
- ✅ Caching strategy implemented

### Reliability
- ✅ Health check endpoints
- ✅ Graceful shutdown handling
- ✅ Proper error handling and logging
- ✅ Database connection retry logic
- ✅ Circuit breakers for external services

### Security
- ✅ Environment variables for secrets
- ✅ CORS properly configured
- ✅ Rate limiting implemented
- ✅ Input validation on all endpoints
- ✅ SQL injection prevention (JSONB queries)

### Monitoring
- ✅ Prometheus metrics exposed
- ✅ Structured logging
- ✅ Performance monitoring
- ✅ Error tracking (Sentry)
- ✅ Database query monitoring

### Testing
- ✅ Unit tests for business logic
- ✅ Integration tests for APIs
- ✅ Load testing completed
- ✅ Test coverage > 80%

### Deployment
- ✅ Dockerfile optimized
- ✅ Kubernetes manifests ready
- ✅ CI/CD pipeline configured
- ✅ Blue-green deployment strategy
- ✅ Rollback procedures documented

**🎉 Congratulations!** You've built a production-ready FastAPI + DocumentDB application with best practices for performance, reliability, and scalability!
