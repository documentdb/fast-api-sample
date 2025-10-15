"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Database
from app.routers import products, customers, orders, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database connection and create indexes
    - Shutdown: Close database connection
    """
    # Startup: Initialize database
    await Database.connect_db()
    print("✓ Database initialized successfully")
    
    yield
    
    # Shutdown: Close database connection
    await Database.close_db()
    print("✓ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    E-commerce API built with FastAPI and DocumentDB.
    
    ## Features
    
    * **Products**: Manage product catalog with categories, pricing, and inventory
    * **Customers**: Customer account management
    * **Orders**: Order processing with automatic stock management
    
    ## Key Technologies
    
    * FastAPI for modern async API development
    * DocumentDB (MongoDB-compatible) for flexible document storage
    * Beanie ODM for type-safe database operations
    * Pydantic for data validation
    
    ## Getting Started
    
    1. Browse the API documentation below
    2. Try out endpoints using the interactive docs
    3. Check out the [GitHub repository](https://github.com/documentdb/documentdb) for more information
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - API health check.
    """
    return JSONResponse(
        content={
            "message": "Welcome to the E-commerce API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "status": "healthy",
        }
    )


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the API and database connection.
    """
    try:
        # Check database connection
        db_status = "healthy" if Database.client else "disconnected"
        
        return JSONResponse(
            content={
                "status": "healthy",
                "database": db_status,
                "version": settings.APP_VERSION,
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": settings.APP_VERSION,
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
