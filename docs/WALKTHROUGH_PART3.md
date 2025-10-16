# FastAPI + DocumentDB: Part 3 - DocumentDB Superpowers 🚀

> **Prerequisites**: Completed Part 1 and Part 2 of the walkthrough

This section explores DocumentDB's unique capabilities that set it apart from traditional MongoDB deployments, leveraging its PostgreSQL foundation for advanced features.

---

## Part 3: DocumentDB Superpowers

### Step 6: Vector Search for AI-Powered Recommendations

**Scenario**: Add semantic product search and "similar products" recommendations using vector embeddings.

#### 6.1 Understanding Vector Embeddings

**What are vector embeddings?**

Vector embeddings are numerical representations of data (text, images, etc.) in high-dimensional space. Similar items have similar vector representations.

```
Text: "USB-C charging cable, 2 meters, braided"
         ↓ (embedding model)
Vector: [0.234, -0.891, 0.456, ..., 0.123]  // 384 dimensions

Text: "USB-C cable for charging, braided, 2m"
         ↓ (embedding model)
Vector: [0.228, -0.887, 0.462, ..., 0.119]  // Very similar!

Text: "Wireless headphones with noise cancellation"
         ↓ (embedding model)
Vector: [-0.654, 0.234, -0.123, ..., 0.987]  // Very different
```

**Why use vector search?**
- **Semantic understanding**: Finds items with similar meaning, not just keywords
- **Typo-tolerant**: Works even with misspellings
- **Cross-lingual**: Can work across languages
- **Recommendation engines**: "Customers who bought X also liked Y"

#### 6.2 Creating Vector Indexes (HNSW vs IVF)

DocumentDB supports two types of vector indexes:

**HNSW (Hierarchical Navigable Small World)**
- **Best for**: High accuracy requirements
- **Speed**: Slower indexing, faster queries
- **Parameters**:
  - `m`: Max connections per layer (higher = more accurate, more memory)
  - `efConstruction`: Size of candidate list during index build
  - `efSearch`: Size of candidate list during search

**IVF (Inverted File)**
- **Best for**: Large datasets where speed matters more than perfect accuracy
- **Speed**: Faster indexing, slightly less accurate
- **Parameters**:
  - `numLists`: Number of clusters
  - `nProbes`: Number of clusters to search

**Similarity Metrics:**
- **COS (Cosine)**: Measures angle between vectors (common for text)
- **L2 (Euclidean)**: Measures straight-line distance
- **IP (Inner Product)**: Measures alignment

#### 6.3 Building a FastAPI Endpoint for Similarity Search

**Step 1: Update Product Model with Vector Field**

**File: `backend/app/models/product.py`**

```python
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from beanie import Document, Indexed
from pydantic import Field, field_validator
from bson import Decimal128


class Product(Document):
    """Product document model with vector embeddings."""
    
    name: Indexed(str)
    description: str
    price: Decimal = Field(ge=0, description="Product price must be non-negative")
    sku: Indexed(str, unique=True)
    category: Indexed(str)
    tags: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(ge=0, default=0)
    is_active: bool = Field(default=True)
    image_url: Optional[str] = None
    
    # Vector embedding for semantic search (384 dimensions for all-MiniLM-L6-v2 model)
    embedding: List[float] = Field(
        default_factory=list,
        description="Vector embedding for semantic similarity search"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        """Convert price to Decimal, handling Decimal128 from MongoDB."""
        if isinstance(v, Decimal128):
            return Decimal(str(v.to_decimal()))
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v
    
    @field_validator("embedding", mode="before")
    @classmethod
    def validate_embedding(cls, v):
        """Ensure embedding is a list of floats."""
        if v and not isinstance(v, list):
            raise ValueError("Embedding must be a list of floats")
        return v
    
    class Settings:
        name = "products"
        indexes = [
            "name",
            "sku",
            "category",
            # Vector index will be created separately via DocumentDB command
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 199.99,
                "sku": "WH-1000XM4",
                "category": "Electronics",
                "tags": ["audio", "wireless", "noise-cancelling"],
                "stock_quantity": 50,
                "is_active": True,
                "image_url": "https://example.com/images/headphones.jpg",
                "embedding": []  # Will be generated automatically
            }
        }
```

**Step 2: Create Embedding Utility**

**File: `backend/app/utils/embeddings.py`**

```python
"""
Utility functions for generating vector embeddings.

For production, consider using:
- OpenAI Embeddings API
- Sentence Transformers (self-hosted)
- Azure OpenAI Service
- Google Vertex AI

This example uses a simple local model for demonstration.
"""

from typing import List, Union
import numpy as np


class EmbeddingGenerator:
    """Simple embedding generator for demonstration purposes."""
    
    def __init__(self, dimensions: int = 384):
        """
        Initialize the embedding generator.
        
        Args:
            dimensions: Number of dimensions for the embedding vector
        """
        self.dimensions = dimensions
        self._model = None
    
    def _load_model(self):
        """
        Load the embedding model.
        
        For production, uncomment this to use sentence-transformers:
        
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer('all-MiniLM-L6-v2')
        """
        # For now, we'll use a deterministic hash-based approach for demo
        # This is NOT suitable for production but works for testing
        pass
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        # DEMO VERSION: Simple hash-based pseudo-embedding
        # Replace with actual model in production!
        
        # Normalize text
        text = text.lower().strip()
        
        # Generate pseudo-embedding based on text hash
        # This creates consistent vectors for same text
        np.random.seed(abs(hash(text)) % (2**32))
        embedding = np.random.randn(self.dimensions).tolist()
        
        # Normalize to unit vector (common for cosine similarity)
        norm = np.linalg.norm(embedding)
        embedding = [float(x / norm) for x in embedding]
        
        return embedding
    
    def generate_embedding_from_product(
        self,
        name: str,
        description: str = "",
        tags: List[str] = None
    ) -> List[float]:
        """
        Generate embedding from product information.
        
        Combines name, description, and tags into a single text representation.
        """
        tags = tags or []
        
        # Combine all text fields with weights
        text_parts = [
            f"{name} {name}",  # Name twice for emphasis
            description,
            " ".join(tags),
        ]
        
        combined_text = " ".join(filter(None, text_parts))
        return self.generate_embedding(combined_text)


# Global instance
embedding_generator = EmbeddingGenerator(dimensions=384)


# Convenience functions
def generate_product_embedding(
    name: str,
    description: str = "",
    tags: List[str] = None
) -> List[float]:
    """Generate embedding for a product."""
    return embedding_generator.generate_embedding_from_product(
        name, description, tags
    )
```

**For Production**: Install sentence-transformers:
```powershell
pip install sentence-transformers
```

Then update the `_load_model` method to use a real model.

**Step 3: Create Vector Index in DocumentDB**

We need to create a vector index using DocumentDB's MongoDB-compatible commands:

**File: `scripts/create_vector_index.py`**

```python
"""
Script to create vector search index in DocumentDB.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings


async def create_vector_index():
    """Create HNSW vector index on products collection."""
    
    # Connect to DocumentDB
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    collection = db["products"]
    
    try:
        # Create HNSW vector index
        print("Creating HNSW vector index...")
        
        # Using DocumentDB's custom index creation command
        result = await db.command({
            "createIndexes": "products",
            "indexes": [
                {
                    "key": {"embedding": "cosmosSearch"},
                    "name": "product_embedding_hnsw",
                    "cosmosSearchOptions": {
                        "kind": "vector-hnsw",
                        "m": 16,                    # Max connections per layer
                        "efConstruction": 64,       # Build quality
                        "similarity": "COS",        # Cosine similarity
                        "dimensions": 384           # Vector dimensions
                    }
                }
            ]
        })
        
        print(f"✓ Vector index created successfully: {result}")
        
        # Verify index exists
        indexes = await collection.list_indexes().to_list(length=None)
        print("\nExisting indexes:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
    except Exception as e:
        print(f"✗ Error creating vector index: {e}")
        raise
    
    finally:
        client.close()


async def create_ivf_index():
    """Create IVF vector index (alternative to HNSW)."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    
    try:
        print("Creating IVF vector index...")
        
        result = await db.command({
            "createIndexes": "products",
            "indexes": [
                {
                    "key": {"embedding": "cosmosSearch"},
                    "name": "product_embedding_ivf",
                    "cosmosSearchOptions": {
                        "kind": "vector-ivf",
                        "numLists": 100,        # Number of clusters
                        "similarity": "COS",    # Cosine similarity
                        "dimensions": 384       # Vector dimensions
                    }
                }
            ]
        })
        
        print(f"✓ IVF vector index created successfully: {result}")
        
    except Exception as e:
        print(f"✗ Error creating IVF index: {e}")
        raise
    
    finally:
        client.close()


if __name__ == "__main__":
    print("DocumentDB Vector Index Creation")
    print("=" * 50)
    print(f"Database: {settings.DOCUMENTDB_DB_NAME}")
    print(f"Collection: products")
    print()
    
    # Create HNSW index (recommended for most cases)
    asyncio.run(create_vector_index())
    
    # Optionally create IVF index for comparison
    # asyncio.run(create_ivf_index())
```

**Run the script:**
```powershell
python scripts/create_vector_index.py
```

**Step 4: Auto-Generate Embeddings on Product Creation**

**Update `backend/app/routers/products.py`:**

```python
from app.utils.embeddings import generate_product_embedding

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product_data: ProductCreate) -> ProductResponse:
    """Create a new product in the catalog with automatic embedding generation."""
    
    # Check if SKU already exists
    existing_product = await Product.find_one(Product.sku == product_data.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists",
        )
    
    # Create product
    product = Product(**product_data.model_dump())
    
    # Generate embedding automatically
    product.embedding = generate_product_embedding(
        name=product.name,
        description=product.description or "",
        tags=product.tags
    )
    
    await product.insert()
    
    return ProductResponse(**product.model_dump())
```

**Step 5: Create Vector Search Endpoints**

**File: `backend/app/routers/vector_search.py`**

```python
"""
Vector search endpoints for semantic product discovery.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models.product import Product
from app.schemas.product import ProductResponse
from app.utils.embeddings import generate_product_embedding

router = APIRouter(prefix="/search", tags=["vector-search"])


@router.get("/similar/{product_id}", response_model=List[ProductResponse])
async def find_similar_products(
    product_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of similar products"),
    min_score: float = Query(
        0.5,
        ge=0,
        le=1,
        description="Minimum similarity score (0-1)"
    )
):
    """
    Find products similar to the given product using vector similarity search.
    
    Uses DocumentDB's vector search capabilities with HNSW indexing for
    fast and accurate semantic similarity matching.
    
    Args:
        product_id: ID of the product to find similar items for
        limit: Maximum number of similar products to return
        min_score: Minimum similarity score threshold (0-1)
    
    Returns:
        List of similar products sorted by similarity score
    """
    # Get the source product
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    
    if not product.embedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product does not have an embedding vector",
        )
    
    # Build aggregation pipeline for vector search
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": product.embedding,
                    "path": "embedding",
                    "k": limit + 1,  # +1 because source product will be included
                    "efSearch": 100   # Search quality parameter for HNSW
                }
            }
        },
        {
            "$match": {
                "_id": {"$ne": product_id},  # Exclude the source product
                "is_active": True
            }
        },
        {
            "$addFields": {
                "similarity_score": {"$meta": "searchScore"}
            }
        },
        {
            "$match": {
                "similarity_score": {"$gte": min_score}
            }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "description": 1,
                "price": 1,
                "category": 1,
                "tags": 1,
                "stock_quantity": 1,
                "image_url": 1,
                "similarity_score": 1
            }
        }
    ]
    
    # Execute aggregation
    similar_products = await Product.aggregate(pipeline).to_list()
    
    return [ProductResponse(**p) for p in similar_products]


@router.get("/semantic", response_model=List[ProductResponse])
async def semantic_search(
    query: str = Query(..., min_length=2, description="Search query text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    min_score: float = Query(0.3, ge=0, le=1, description="Minimum similarity")
):
    """
    Semantic search for products based on natural language query.
    
    Uses vector embeddings to find products that match the semantic meaning
    of the query, not just keyword matching.
    
    Examples:
        - "cable for charging my phone" → finds USB cables
        - "something to listen to music" → finds headphones/speakers
        - "wireless audio device" → finds bluetooth headphones
    
    Args:
        query: Natural language search query
        category: Optional category filter
        limit: Maximum number of results
        min_score: Minimum similarity threshold
    
    Returns:
        List of products matching the semantic query
    """
    # Generate embedding for the search query
    query_embedding = generate_product_embedding(
        name=query,
        description="",
        tags=[]
    )
    
    # Build aggregation pipeline
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "embedding",
                    "k": limit * 2,  # Search more to filter
                    "efSearch": 100
                }
            }
        },
        {
            "$match": {
                "is_active": True
            }
        },
        {
            "$addFields": {
                "similarity_score": {"$meta": "searchScore"}
            }
        },
        {
            "$match": {
                "similarity_score": {"$gte": min_score}
            }
        }
    ]
    
    # Add category filter if specified
    if category:
        pipeline.insert(1, {
            "$match": {"category": category}
        })
    
    # Add limit and projection
    pipeline.extend([
        {"$limit": limit},
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "description": 1,
                "price": 1,
                "category": 1,
                "tags": 1,
                "stock_quantity": 1,
                "image_url": 1,
                "similarity_score": 1
            }
        }
    ])
    
    # Execute search
    results = await Product.aggregate(pipeline).to_list()
    
    return [ProductResponse(**p) for p in results]


@router.get("/recommendations/{customer_email}")
async def get_personalized_recommendations(
    customer_email: str,
    limit: int = Query(10, ge=1, le=20)
):
    """
    Get personalized product recommendations based on customer's order history.
    
    Analyzes customer's past purchases and finds similar products they might like.
    
    Args:
        customer_email: Customer's email address
        limit: Number of recommendations
    
    Returns:
        Recommended products with similarity scores
    """
    from app.models.order import Order
    
    # Get customer's order history
    orders = await Order.find(
        Order.customer_email == customer_email,
        Order.status == {"$in": ["delivered", "shipped"]}
    ).to_list()
    
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No order history found for this customer",
        )
    
    # Extract product IDs from orders
    purchased_product_ids = set()
    for order in orders:
        for item in order.items:
            purchased_product_ids.add(str(item.product_id))
    
    # Get purchased products
    purchased_products = await Product.find(
        {"_id": {"$in": list(purchased_product_ids)}}
    ).to_list()
    
    if not purchased_products:
        return []
    
    # Calculate average embedding from purchased products
    valid_embeddings = [
        p.embedding for p in purchased_products
        if p.embedding and len(p.embedding) > 0
    ]
    
    if not valid_embeddings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No embeddings available for purchased products",
        )
    
    # Average the embeddings (simple approach)
    import numpy as np
    avg_embedding = np.mean(valid_embeddings, axis=0).tolist()
    
    # Find similar products
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": avg_embedding,
                    "path": "embedding",
                    "k": limit * 2,
                    "efSearch": 100
                }
            }
        },
        {
            "$match": {
                "_id": {"$nin": list(purchased_product_ids)},  # Exclude already purchased
                "is_active": True,
                "stock_quantity": {"$gt": 0}  # Only in-stock items
            }
        },
        {
            "$addFields": {
                "recommendation_score": {"$meta": "searchScore"}
            }
        },
        {"$limit": limit},
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "description": 1,
                "price": 1,
                "category": 1,
                "image_url": 1,
                "recommendation_score": 1
            }
        }
    ]
    
    recommendations = await Product.aggregate(pipeline).to_list()
    
    return {
        "customer_email": customer_email,
        "based_on_purchases": len(purchased_product_ids),
        "recommendations": recommendations
    }
```

**Step 6: Register the Router**

**Update `backend/app/main.py`:**

```python
from app.routers import products, customers, orders, admin, reviews, vector_search

app.include_router(vector_search.router, prefix="/api/v1")
```

#### 6.4 Testing Vector Search

**Restart the server:**
```powershell
uvicorn app.main:app --reload
```

**Test the endpoints:**

1. **Create products with embeddings:**
   ```
   POST /api/v1/products
   ```
   Create a few products (embeddings auto-generated)

2. **Find similar products:**
   ```
   GET /api/v1/search/similar/{product_id}?limit=5
   ```

3. **Semantic search:**
   ```
   GET /api/v1/search/semantic?query=wireless audio device&limit=10
   ```

4. **Personalized recommendations:**
   ```
   GET /api/v1/search/recommendations/customer@example.com?limit=10
   ```

#### 6.5 Hands-On Exercise: Build a "Customers Also Viewed" Feature

**Goal**: Track product views and recommend products based on what other customers viewed.

**Implementation Steps:**

1. **Create a ProductView model** to track views
2. **Add endpoint** to record views
3. **Build recommendation algorithm** using collaborative filtering + vector search
4. **Create API endpoint** that combines both signals

This exercise combines DocumentDB's aggregation pipeline capabilities with vector search for powerful recommendations!

---

### Summary: What We've Learned

✅ **Vector Embeddings**: Convert text to numerical representations  
✅ **Vector Indexes**: HNSW vs IVF trade-offs  
✅ **Semantic Search**: Find similar products by meaning, not just keywords  
✅ **Similarity Metrics**: Cosine, L2, Inner Product  
✅ **FastAPI Integration**: Building async vector search endpoints  
✅ **Real-world Applications**: Product recommendations, semantic search

**Next**: Step 7 - Geospatial Queries for location-based features!

---

### Step 7: Geospatial Queries for Location-Based Features

**Scenario**: Build a store locator and delivery zone verification system using DocumentDB's geospatial capabilities (powered by PostGIS).

#### 7.1 Understanding Geospatial Data in DocumentDB

DocumentDB leverages **PostgreSQL's PostGIS extension** for advanced geospatial operations, giving you enterprise-grade location features.

**GeoJSON Format:**
```json
{
  "type": "Point",
  "coordinates": [longitude, latitude]
}
```

**Important**: Coordinates are `[longitude, latitude]` (x, y), not the other way around!

**Common Geospatial Types:**
- **Point**: Single location (store, customer address)
- **Polygon**: Area (delivery zone, city boundary)
- **LineString**: Route (delivery path)
- **MultiPoint**: Multiple locations (chain stores)

**Index Types:**
- **2d**: Flat plane calculations (fast, less accurate for large distances)
- **2dsphere**: Spherical Earth calculations (accurate, slower)

#### 7.2 Creating a Store Model with Geospatial Data

**File: `backend/app/models/store.py`**

```python
"""
Store location model with geospatial support.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, time
from beanie import Document, Indexed
from pydantic import Field, field_validator
from bson import ObjectId


class Store(Document):
    """Physical store location with geospatial capabilities."""
    
    name: str = Field(..., min_length=1, max_length=200)
    store_code: Indexed(str, unique=True) = Field(..., description="Unique store identifier")
    
    # Geospatial location (GeoJSON format)
    # coordinates: [longitude, latitude]
    location: Dict[str, Any] = Field(
        ...,
        description="GeoJSON Point with [longitude, latitude] coordinates"
    )
    
    # Address information
    address: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    
    # Store details
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    
    # Operating hours (simplified - could be more complex)
    opening_time: Optional[time] = Field(None, description="Store opening time")
    closing_time: Optional[time] = Field(None, description="Store closing time")
    
    # Delivery capabilities
    offers_delivery: bool = Field(default=True)
    delivery_radius_km: float = Field(
        default=10.0,
        ge=0,
        description="Delivery radius in kilometers"
    )
    
    # Inventory
    inventory_product_ids: List[str] = Field(
        default_factory=list,
        description="Product IDs available at this store"
    )
    
    # Status
    is_active: bool = Field(default=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        """Validate GeoJSON Point format."""
        if not isinstance(v, dict):
            raise ValueError("Location must be a dictionary")
        
        if v.get("type") != "Point":
            raise ValueError("Location type must be 'Point'")
        
        coords = v.get("coordinates")
        if not coords or len(coords) != 2:
            raise ValueError("Coordinates must be [longitude, latitude]")
        
        lon, lat = coords
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        
        return v
    
    @property
    def longitude(self) -> float:
        """Get longitude from location."""
        return self.location["coordinates"][0]
    
    @property
    def latitude(self) -> float:
        """Get latitude from location."""
        return self.location["coordinates"][1]
    
    class Settings:
        name = "stores"
        indexes = [
            "store_code",
            "city",
            "state",
            # Geospatial index created separately
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Downtown Seattle Store",
                "store_code": "SEA-DT-001",
                "location": {
                    "type": "Point",
                    "coordinates": [-122.3321, 47.6062]  # [longitude, latitude]
                },
                "address": "1234 Pike St",
                "city": "Seattle",
                "state": "WA",
                "postal_code": "98101",
                "phone": "+1-206-555-0123",
                "offers_delivery": True,
                "delivery_radius_km": 15.0
            }
        }
```

**File: `backend/app/schemas/store.py`**

```python
"""
Store API schemas.
"""

from typing import Optional, List, Dict, Any
from datetime import time
from pydantic import BaseModel, Field, field_validator


class LocationInput(BaseModel):
    """GeoJSON Point input."""
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    
    def to_geojson(self) -> Dict[str, Any]:
        """Convert to GeoJSON format."""
        return {
            "type": "Point",
            "coordinates": [self.longitude, self.latitude]
        }


class StoreCreate(BaseModel):
    """Schema for creating a new store."""
    name: str = Field(..., min_length=1, max_length=200)
    store_code: str = Field(..., min_length=1)
    location: LocationInput
    address: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    offers_delivery: bool = True
    delivery_radius_km: float = Field(default=10.0, ge=0)


class StoreUpdate(BaseModel):
    """Schema for updating a store."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[LocationInput] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    offers_delivery: Optional[bool] = None
    delivery_radius_km: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    """Schema for store API responses."""
    id: str = Field(alias="_id")
    name: str
    store_code: str
    location: Dict[str, Any]
    address: str
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    offers_delivery: bool
    delivery_radius_km: float
    is_active: bool
    distance_km: Optional[float] = Field(
        None,
        description="Distance from query point (populated by geospatial queries)"
    )
    
    class Config:
        populate_by_name = True


class NearbyStoresQuery(BaseModel):
    """Query parameters for finding nearby stores."""
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    max_distance_km: float = Field(default=50.0, ge=0, le=500)
    limit: int = Field(default=10, ge=1, le=100)
```

#### 7.3 Creating Geospatial Indexes

**File: `scripts/create_geospatial_index.py`**

```python
"""
Script to create 2dsphere geospatial index for stores collection.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings


async def create_geospatial_index():
    """Create 2dsphere index on stores collection."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    collection = db["stores"]
    
    try:
        print("Creating 2dsphere geospatial index...")
        
        # Create the geospatial index
        result = await collection.create_index(
            [("location", "2dsphere")],
            name="store_location_2dsphere"
        )
        
        print(f"✓ Geospatial index created: {result}")
        
        # Verify index
        indexes = await collection.list_indexes().to_list(length=None)
        print("\nExisting indexes on stores collection:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
    except Exception as e:
        print(f"✗ Error creating geospatial index: {e}")
        raise
    
    finally:
        client.close()


if __name__ == "__main__":
    print("DocumentDB Geospatial Index Creation")
    print("=" * 50)
    asyncio.run(create_geospatial_index())
```

**Run the script:**
```powershell
python scripts/create_geospatial_index.py
```

#### 7.4 Building Geospatial Query Endpoints

**File: `backend/app/routers/stores.py`**

```python
"""
Store location and geospatial query endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from bson import ObjectId

from app.models.store import Store
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    NearbyStoresQuery
)

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(store_data: StoreCreate):
    """Create a new store location."""
    
    # Check if store code exists
    existing = await Store.find_one(Store.store_code == store_data.store_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Store with code '{store_data.store_code}' already exists"
        )
    
    # Convert location input to GeoJSON
    store_dict = store_data.model_dump()
    store_dict["location"] = store_data.location.to_geojson()
    
    store = Store(**store_dict)
    await store.insert()
    
    return StoreResponse(**store.model_dump())


@router.get("/nearby", response_model=List[StoreResponse])
async def find_nearby_stores(
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    max_distance_km: float = Query(50.0, ge=0, le=500, description="Maximum distance in km"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    only_active: bool = Query(True, description="Only return active stores"),
    offers_delivery: Optional[bool] = Query(None, description="Filter by delivery availability")
):
    """
    Find stores near a given location using geospatial queries.
    
    Uses DocumentDB's 2dsphere index with PostGIS backend for accurate
    distance calculations on a spherical Earth model.
    
    Example:
        GET /api/v1/stores/nearby?longitude=-122.3321&latitude=47.6062&max_distance_km=25
    """
    
    # Build match conditions
    match_conditions = {}
    if only_active:
        match_conditions["is_active"] = True
    if offers_delivery is not None:
        match_conditions["offers_delivery"] = offers_delivery
    
    # Aggregation pipeline with $geoNear
    # $geoNear must be the first stage in the pipeline
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "distanceField": "distance_meters",
                "maxDistance": max_distance_km * 1000,  # Convert km to meters
                "spherical": True,  # Use spherical calculations
                "key": "location"
            }
        }
    ]
    
    # Add match stage if we have conditions
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    # Add distance in km field and project
    pipeline.extend([
        {
            "$addFields": {
                "distance_km": {
                    "$divide": ["$distance_meters", 1000]
                }
            }
        },
        {
            "$limit": limit
        }
    ])
    
    # Execute aggregation
    stores = await Store.aggregate(pipeline).to_list()
    
    return [StoreResponse(**store) for store in stores]


@router.get("/within-polygon", response_model=List[StoreResponse])
async def find_stores_in_area(
    polygon_coords: str = Query(
        ...,
        description="Polygon coordinates as JSON string: [[[lon,lat],[lon,lat],...]]"
    )
):
    """
    Find stores within a geographic polygon (e.g., city boundary, delivery zone).
    
    The polygon should be a closed loop (first and last coordinates must match).
    
    Example polygon (square around Seattle):
        [
          [[-122.4, 47.5], [-122.2, 47.5], [-122.2, 47.7], [-122.4, 47.7], [-122.4, 47.5]]
        ]
    """
    import json
    
    try:
        coordinates = json.loads(polygon_coords)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid polygon coordinates format"
        )
    
    # Query using $geoWithin
    pipeline = [
        {
            "$match": {
                "location": {
                    "$geoWithin": {
                        "$geometry": {
                            "type": "Polygon",
                            "coordinates": coordinates
                        }
                    }
                },
                "is_active": True
            }
        }
    ]
    
    stores = await Store.aggregate(pipeline).to_list()
    
    return [StoreResponse(**store) for store in stores]


@router.get("/{store_id}/can-deliver-to")
async def check_delivery_availability(
    store_id: str,
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90)
):
    """
    Check if a store can deliver to a specific location.
    
    Calculates the actual distance and compares it to the store's delivery radius.
    """
    
    store = await Store.get(store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID '{store_id}' not found"
        )
    
    if not store.offers_delivery:
        return {
            "can_deliver": False,
            "reason": "Store does not offer delivery",
            "store_name": store.name
        }
    
    # Calculate distance using aggregation
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "distanceField": "distance_meters",
                "maxDistance": store.delivery_radius_km * 1000 * 2,  # Search wider
                "spherical": True,
                "key": "location",
                "query": {"_id": ObjectId(store_id)}
            }
        },
        {
            "$addFields": {
                "distance_km": {"$divide": ["$distance_meters", 1000]}
            }
        }
    ]
    
    results = await Store.aggregate(pipeline).to_list()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate distance"
        )
    
    distance_km = results[0]["distance_km"]
    can_deliver = distance_km <= store.delivery_radius_km
    
    return {
        "can_deliver": can_deliver,
        "store_name": store.name,
        "store_location": {
            "latitude": store.latitude,
            "longitude": store.longitude
        },
        "delivery_address": {
            "latitude": latitude,
            "longitude": longitude
        },
        "distance_km": round(distance_km, 2),
        "delivery_radius_km": store.delivery_radius_km,
        "message": (
            f"Delivery available! Distance: {distance_km:.2f} km"
            if can_deliver
            else f"Outside delivery zone. Distance: {distance_km:.2f} km, "
                 f"Max: {store.delivery_radius_km} km"
        )
    }


@router.get("/closest-with-product/{product_id}")
async def find_closest_store_with_product(
    product_id: str,
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    max_distance_km: float = Query(100.0, ge=0, le=500)
):
    """
    Find the closest store that has a specific product in stock.
    
    Combines geospatial queries with inventory filtering.
    """
    
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "distanceField": "distance_meters",
                "maxDistance": max_distance_km * 1000,
                "spherical": True,
                "key": "location",
                "query": {
                    "is_active": True,
                    "inventory_product_ids": product_id
                }
            }
        },
        {
            "$addFields": {
                "distance_km": {"$divide": ["$distance_meters", 1000]}
            }
        },
        {"$limit": 1}
    ]
    
    results = await Store.aggregate(pipeline).to_list()
    
    if not results:
        return {
            "found": False,
            "message": f"No stores within {max_distance_km} km have this product in stock"
        }
    
    store = results[0]
    
    return {
        "found": True,
        "store": StoreResponse(**store),
        "distance_km": round(store["distance_km"], 2)
    }
```

#### 7.5 Loading Sample Store Data

**File: `scripts/load_sample_stores.py`**

```python
"""
Load sample store locations for testing geospatial features.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings


# Sample stores across major US cities
SAMPLE_STORES = [
    {
        "name": "Downtown Seattle Store",
        "store_code": "SEA-DT-001",
        "location": {"type": "Point", "coordinates": [-122.3321, 47.6062]},
        "address": "1234 Pike St",
        "city": "Seattle",
        "state": "WA",
        "postal_code": "98101",
        "phone": "+1-206-555-0123",
        "offers_delivery": True,
        "delivery_radius_km": 15.0,
        "is_active": True
    },
    {
        "name": "Capitol Hill Seattle Store",
        "store_code": "SEA-CH-002",
        "location": {"type": "Point", "coordinates": [-122.3226, 47.6205]},
        "address": "567 Broadway E",
        "city": "Seattle",
        "state": "WA",
        "postal_code": "98102",
        "phone": "+1-206-555-0124",
        "offers_delivery": True,
        "delivery_radius_km": 10.0,
        "is_active": True
    },
    {
        "name": "Bellevue Store",
        "store_code": "BEL-001",
        "location": {"type": "Point", "coordinates": [-122.2015, 47.6101]},
        "address": "789 Bellevue Way NE",
        "city": "Bellevue",
        "state": "WA",
        "postal_code": "98004",
        "phone": "+1-425-555-0125",
        "offers_delivery": True,
        "delivery_radius_km": 12.0,
        "is_active": True
    },
    {
        "name": "Portland Downtown Store",
        "store_code": "PDX-DT-001",
        "location": {"type": "Point", "coordinates": [-122.6765, 45.5231]},
        "address": "321 SW Morrison St",
        "city": "Portland",
        "state": "OR",
        "postal_code": "97204",
        "phone": "+1-503-555-0201",
        "offers_delivery": True,
        "delivery_radius_km": 20.0,
        "is_active": True
    },
    {
        "name": "San Francisco Mission Store",
        "store_code": "SFO-MS-001",
        "location": {"type": "Point", "coordinates": [-122.4194, 37.7749]},
        "address": "456 Mission St",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94105",
        "phone": "+1-415-555-0301",
        "offers_delivery": True,
        "delivery_radius_km": 8.0,
        "is_active": True
    },
]


async def load_stores():
    """Load sample stores into DocumentDB."""
    
    client = AsyncIOMotorClient(
        settings.DOCUMENTDB_URL,
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    
    db = client[settings.DOCUMENTDB_DB_NAME]
    collection = db["stores"]
    
    try:
        # Clear existing stores
        result = await collection.delete_many({})
        print(f"Cleared {result.deleted_count} existing stores")
        
        # Insert sample stores
        result = await collection.insert_many(SAMPLE_STORES)
        print(f"✓ Inserted {len(result.inserted_ids)} stores")
        
        # Verify
        count = await collection.count_documents({})
        print(f"Total stores in database: {count}")
        
    except Exception as e:
        print(f"✗ Error loading stores: {e}")
        raise
    
    finally:
        client.close()


if __name__ == "__main__":
    print("Loading Sample Stores")
    print("=" * 50)
    asyncio.run(load_stores())
```

**Run the script:**
```powershell
python scripts/load_sample_stores.py
```

#### 7.6 Testing Geospatial Queries

**Register the router in `backend/app/main.py`:**
```python
from app.routers import products, customers, orders, admin, reviews, vector_search, stores

app.include_router(stores.router, prefix="/api/v1")
```

**Test the endpoints:**

1. **Find nearby stores (from Seattle downtown):**
   ```
   GET /api/v1/stores/nearby?longitude=-122.3321&latitude=47.6062&max_distance_km=25
   ```

2. **Check delivery availability:**
   ```
   GET /api/v1/stores/{store_id}/can-deliver-to?longitude=-122.35&latitude=47.62
   ```

3. **Find closest store with product:**
   ```
   GET /api/v1/stores/closest-with-product/{product_id}?longitude=-122.3321&latitude=47.6062
   ```

#### 7.7 Hands-On Exercise: Build a Store Locator UI Component

**Goal**: Create a full store locator feature with map integration.

**Requirements:**
1. Add a "Find Stores Near Me" endpoint that uses browser geolocation
2. Calculate estimated delivery time based on distance
3. Show stores on a map (integrate with Leaflet or Google Maps)
4. Add filtering by store features (open now, has parking, etc.)

**Bonus Challenge**: Implement dynamic delivery zones using polygon queries!

---

### Step 8: Advanced Aggregation Pipelines

**Scenario**: Build powerful analytics and reporting using DocumentDB's aggregation framework (leveraging PostgreSQL backend performance).

#### 8.1 Understanding Aggregation Pipelines

**What are aggregation pipelines?**

Pipelines are a sequence of data transformation stages. Data flows through each stage, getting transformed along the way.

```
Documents → [$match] → [$group] → [$sort] → [$project] → Results
```

**Common Stages:**
- **$match**: Filter documents (like WHERE in SQL)
- **$group**: Aggregate by field (like GROUP BY)
- **$sort**: Order results
- **$project**: Shape output (select fields)
- **$lookup**: Join with other collections
- **$unwind**: Flatten arrays
- **$facet**: Multiple pipelines in parallel
- **$bucket**: Group by ranges

**Why use aggregations?**
- **Performance**: Processed in database (no data transfer)
- **PostgreSQL power**: DocumentDB leverages PostgreSQL for complex calculations
- **Real-time analytics**: Fast enough for live dashboards
- **Complex queries**: Multi-stage transformations in one query

#### 8.2 Building Sales Analytics Endpoints

**File: `backend/app/routers/analytics.py`**

```python
"""
Analytics and reporting endpoints using aggregation pipelines.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from decimal import Decimal

from app.models.order import Order
from app.models.product import Product
from app.models.customer import Customer

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sales-summary")
async def get_sales_summary(
    start_date: Optional[datetime] = Query(
        None,
        description="Start date for analysis (default: 30 days ago)"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="End date for analysis (default: now)"
    ),
    group_by: str = Query(
        "day",
        regex="^(day|week|month)$",
        description="Group results by time period"
    )
):
    """
    Get sales summary with revenue, order count, and average order value.
    
    This demonstrates multi-stage aggregation with date grouping.
    """
    
    # Default date range: last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Determine date grouping format
    date_format = {
        "day": "%Y-%m-%d",
        "week": "%Y-W%U",
        "month": "%Y-%m"
    }[group_by]
    
    pipeline = [
        # Stage 1: Filter by date range and completed orders
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$in": ["delivered", "shipped"]}
            }
        },
        # Stage 2: Group by date period
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": date_format,
                        "date": "$created_at"
                    }
                },
                "total_revenue": {"$sum": "$total_amount"},
                "order_count": {"$sum": 1},
                "unique_customers": {"$addToSet": "$customer_email"},
                "total_items_sold": {
                    "$sum": {
                        "$sum": "$items.quantity"
                    }
                }
            }
        },
        # Stage 3: Calculate average order value
        {
            "$addFields": {
                "average_order_value": {
                    "$divide": ["$total_revenue", "$order_count"]
                },
                "unique_customer_count": {"$size": "$unique_customers"}
            }
        },
        # Stage 4: Sort by date
        {
            "$sort": {"_id": 1}
        },
        # Stage 5: Format output
        {
            "$project": {
                "_id": 0,
                "period": "$_id",
                "total_revenue": {"$round": ["$total_revenue", 2]},
                "order_count": 1,
                "average_order_value": {"$round": ["$average_order_value", 2]},
                "total_items_sold": 1,
                "unique_customer_count": 1
            }
        }
    ]
    
    results = await Order.aggregate(pipeline).to_list()
    
    # Calculate overall summary
    overall_revenue = sum(r["total_revenue"] for r in results)
    overall_orders = sum(r["order_count"] for r in results)
    
    return {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "group_by": group_by
        },
        "overall_summary": {
            "total_revenue": round(overall_revenue, 2),
            "total_orders": overall_orders,
            "average_order_value": (
                round(overall_revenue / overall_orders, 2) if overall_orders > 0 else 0
            )
        },
        "breakdown": results
    }


@router.get("/top-products")
async def get_top_selling_products(
    limit: int = Query(10, ge=1, le=100, description="Number of top products"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get top-selling products with revenue and quantity metrics.
    
    Demonstrates $lookup (join) between orders and products collections.
    """
    
    # Build match conditions
    match_conditions = {
        "status": {"$in": ["delivered", "shipped"]}
    }
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        match_conditions["created_at"] = date_filter
    
    pipeline = [
        # Stage 1: Filter orders
        {"$match": match_conditions},
        
        # Stage 2: Unwind order items to process each item
        {"$unwind": "$items"},
        
        # Stage 3: Group by product
        {
            "$group": {
                "_id": "$items.product_id",
                "total_quantity_sold": {"$sum": "$items.quantity"},
                "total_revenue": {
                    "$sum": {
                        "$multiply": ["$items.price", "$items.quantity"]
                    }
                },
                "order_count": {"$sum": 1}
            }
        },
        
        # Stage 4: Lookup product details (JOIN with products collection)
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "_id",
                "as": "product_info"
            }
        },
        
        # Stage 5: Unwind product info (convert array to object)
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        
        # Stage 6: Filter by category if specified
        *([{"$match": {"product_info.category": category}}] if category else []),
        
        # Stage 7: Calculate metrics
        {
            "$addFields": {
                "average_price": {
                    "$divide": ["$total_revenue", "$total_quantity_sold"]
                }
            }
        },
        
        # Stage 8: Sort by revenue
        {"$sort": {"total_revenue": -1}},
        
        # Stage 9: Limit results
        {"$limit": limit},
        
        # Stage 10: Format output
        {
            "$project": {
                "_id": 0,
                "product_id": "$_id",
                "product_name": "$product_info.name",
                "category": "$product_info.category",
                "sku": "$product_info.sku",
                "total_quantity_sold": 1,
                "total_revenue": {"$round": ["$total_revenue", 2]},
                "average_price": {"$round": ["$average_price", 2]},
                "order_count": 1
            }
        }
    ]
    
    results = await Order.aggregate(pipeline).to_list()
    
    return {
        "top_products": results,
        "filters": {
            "category": category,
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    }


@router.get("/customer-segmentation")
async def analyze_customer_segments():
    """
    Segment customers by spending levels using $bucket aggregation.
    
    Demonstrates $bucket for creating spending tier segments.
    """
    
    pipeline = [
        # Stage 1: Only completed orders
        {
            "$match": {
                "status": {"$in": ["delivered", "shipped"]}
            }
        },
        
        # Stage 2: Group by customer email
        {
            "$group": {
                "_id": "$customer_email",
                "total_spent": {"$sum": "$total_amount"},
                "order_count": {"$sum": 1},
                "first_order_date": {"$min": "$created_at"},
                "last_order_date": {"$max": "$created_at"}
            }
        },
        
        # Stage 3: Calculate customer lifetime
        {
            "$addFields": {
                "customer_lifetime_days": {
                    "$divide": [
                        {"$subtract": ["$last_order_date", "$first_order_date"]},
                        1000 * 60 * 60 * 24  # Convert milliseconds to days
                    ]
                },
                "average_order_value": {
                    "$divide": ["$total_spent", "$order_count"]
                }
            }
        },
        
        # Stage 4: Bucket customers by spending
        {
            "$bucket": {
                "groupBy": "$total_spent",
                "boundaries": [0, 100, 500, 1000, 5000, 100000],
                "default": "VIP",
                "output": {
                    "customer_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_spent"},
                    "avg_orders_per_customer": {"$avg": "$order_count"},
                    "avg_customer_value": {"$avg": "$total_spent"},
                    "avg_order_value": {"$avg": "$average_order_value"}
                }
            }
        },
        
        # Stage 5: Add segment labels
        {
            "$addFields": {
                "segment": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$_id", 0]}, "then": "New/Low Value"},
                            {"case": {"$eq": ["$_id", 100]}, "then": "Bronze"},
                            {"case": {"$eq": ["$_id", 500]}, "then": "Silver"},
                            {"case": {"$eq": ["$_id", 1000]}, "then": "Gold"},
                            {"case": {"$eq": ["$_id", 5000]}, "then": "Platinum"}
                        ],
                        "default": "VIP"
                    }
                },
                "spending_range": {
                    "$concat": [
                        "$",
                        {"$toString": "$_id"},
                        " - $",
                        {
                            "$toString": {
                                "$switch": {
                                    "branches": [
                                        {"case": {"$eq": ["$_id", 0]}, "then": 100},
                                        {"case": {"$eq": ["$_id", 100]}, "then": 500},
                                        {"case": {"$eq": ["$_id", 500]}, "then": 1000},
                                        {"case": {"$eq": ["$_id", 1000]}, "then": 5000},
                                        {"case": {"$eq": ["$_id", 5000]}, "then": 100000}
                                    ],
                                    "default": "∞"
                                }
                            }
                        }
                    ]
                }
            }
        },
        
        # Stage 6: Format output
        {
            "$project": {
                "_id": 0,
                "segment": 1,
                "spending_range": 1,
                "customer_count": 1,
                "total_revenue": {"$round": ["$total_revenue", 2]},
                "avg_orders_per_customer": {"$round": ["$avg_orders_per_customer", 1]},
                "avg_customer_value": {"$round": ["$avg_customer_value", 2]},
                "avg_order_value": {"$round": ["$avg_order_value", 2]}
            }
        }
    ]
    
    segments = await Order.aggregate(pipeline).to_list()
    
    # Calculate totals
    total_customers = sum(s["customer_count"] for s in segments)
    total_revenue = sum(s["total_revenue"] for s in segments)
    
    return {
        "segments": segments,
        "summary": {
            "total_customers": total_customers,
            "total_revenue": round(total_revenue, 2),
            "average_customer_value": (
                round(total_revenue / total_customers, 2) if total_customers > 0 else 0
            )
        }
    }


@router.get("/category-performance")
async def analyze_category_performance():
    """
    Analyze sales performance by product category using $facet for parallel pipelines.
    
    Demonstrates $facet for running multiple aggregations simultaneously.
    """
    
    pipeline = [
        # Stage 1: Filter completed orders
        {
            "$match": {
                "status": {"$in": ["delivered", "shipped"]}
            }
        },
        
        # Stage 2: Unwind items
        {"$unwind": "$items"},
        
        # Stage 3: Lookup product details
        {
            "$lookup": {
                "from": "products",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product"
            }
        },
        
        # Stage 4: Unwind product
        {"$unwind": "$product"},
        
        # Stage 5: Run multiple pipelines in parallel with $facet
        {
            "$facet": {
                # Pipeline 1: Revenue by category
                "revenue_by_category": [
                    {
                        "$group": {
                            "_id": "$product.category",
                            "total_revenue": {
                                "$sum": {
                                    "$multiply": ["$items.price", "$items.quantity"]
                                }
                            },
                            "units_sold": {"$sum": "$items.quantity"}
                        }
                    },
                    {"$sort": {"total_revenue": -1}}
                ],
                
                # Pipeline 2: Average order value by category
                "avg_order_value_by_category": [
                    {
                        "$group": {
                            "_id": {
                                "category": "$product.category",
                                "order_id": "$_id"
                            },
                            "order_value": {
                                "$sum": {
                                    "$multiply": ["$items.price", "$items.quantity"]
                                }
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_id.category",
                            "avg_order_value": {"$avg": "$order_value"}
                        }
                    },
                    {"$sort": {"avg_order_value": -1}}
                ],
                
                # Pipeline 3: Top category combinations (products bought together)
                "category_combinations": [
                    {
                        "$group": {
                            "_id": "$_id",  # Group by order
                            "categories": {"$addToSet": "$product.category"}
                        }
                    },
                    {
                        "$match": {
                            "categories": {"$size": {"$gt": 1}}  # Orders with multiple categories
                        }
                    },
                    {
                        "$group": {
                            "_id": "$categories",
                            "frequency": {"$sum": 1}
                        }
                    },
                    {"$sort": {"frequency": -1}},
                    {"$limit": 5}
                ]
            }
        }
    ]
    
    results = await Order.aggregate(pipeline).to_list()
    
    if not results:
        return {"error": "No data available"}
    
    return {
        "revenue_by_category": results[0]["revenue_by_category"],
        "avg_order_value_by_category": results[0]["avg_order_value_by_category"],
        "top_category_combinations": results[0]["category_combinations"]
    }
```

#### 8.3 Real-time Dashboard with Streaming Aggregations

**File: `backend/app/routers/dashboard.py`**

```python
"""
Real-time dashboard endpoints with efficient aggregations.
"""

from fastapi import APIRouter
from datetime import datetime, timedelta

from app.models.order import Order
from app.models.product import Product
from app.models.customer import Customer

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_dashboard_overview():
    """
    Get comprehensive dashboard overview with multiple metrics in a single query.
    
    Uses $facet to run multiple aggregations in parallel for efficiency.
    """
    
    # Date ranges
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # Run multiple aggregations in parallel
    pipeline = [
        {
            "$facet": {
                # Today's metrics
                "today": [
                    {
                        "$match": {
                            "created_at": {"$gte": today},
                            "status": {"$in": ["delivered", "shipped", "pending", "processing"]}
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "revenue": {"$sum": "$total_amount"},
                            "orders": {"$sum": 1}
                        }
                    }
                ],
                
                # Yesterday's metrics for comparison
                "yesterday": [
                    {
                        "$match": {
                            "created_at": {"$gte": yesterday, "$lt": today},
                            "status": {"$in": ["delivered", "shipped"]}
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "revenue": {"$sum": "$total_amount"},
                            "orders": {"$sum": 1}
                        }
                    }
                ],
                
                # Last 7 days trend
                "last_7_days": [
                    {
                        "$match": {
                            "created_at": {"$gte": last_7_days},
                            "status": {"$in": ["delivered", "shipped"]}
                        }
                    },
                    {
                        "$group": {
                            "_id": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$created_at"
                                }
                            },
                            "revenue": {"$sum": "$total_amount"},
                            "orders": {"$sum": 1}
                        }
                    },
                    {"$sort": {"_id": 1}}
                ],
                
                # Last 30 days metrics
                "last_30_days": [
                    {
                        "$match": {
                            "created_at": {"$gte": last_30_days},
                            "status": {"$in": ["delivered", "shipped"]}
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "revenue": {"$sum": "$total_amount"},
                            "orders": {"$sum": 1},
                            "customers": {"$addToSet": "$customer_email"}
                        }
                    },
                    {
                        "$addFields": {
                            "unique_customers": {"$size": "$customers"}
                        }
                    }
                ]
            }
        }
    ]
    
    results = await Order.aggregate(pipeline).to_list()
    
    if not results:
        return {"error": "No data available"}
    
    data = results[0]
    
    # Extract metrics with defaults
    today_metrics = data["today"][0] if data["today"] else {"revenue": 0, "orders": 0}
    yesterday_metrics = data["yesterday"][0] if data["yesterday"] else {"revenue": 0, "orders": 0}
    monthly_metrics = data["last_30_days"][0] if data["last_30_days"] else {
        "revenue": 0, "orders": 0, "unique_customers": 0
    }
    
    # Calculate growth percentages
    revenue_growth = (
        ((today_metrics["revenue"] - yesterday_metrics["revenue"]) / yesterday_metrics["revenue"] * 100)
        if yesterday_metrics["revenue"] > 0 else 0
    )
    
    order_growth = (
        ((today_metrics["orders"] - yesterday_metrics["orders"]) / yesterday_metrics["orders"] * 100)
        if yesterday_metrics["orders"] > 0 else 0
    )
    
    return {
        "current_period": {
            "today_revenue": round(today_metrics["revenue"], 2),
            "today_orders": today_metrics["orders"],
            "revenue_growth_vs_yesterday": round(revenue_growth, 1),
            "order_growth_vs_yesterday": round(order_growth, 1)
        },
        "monthly_summary": {
            "total_revenue": round(monthly_metrics["revenue"], 2),
            "total_orders": monthly_metrics["orders"],
            "unique_customers": monthly_metrics["unique_customers"],
            "average_order_value": round(
                monthly_metrics["revenue"] / monthly_metrics["orders"], 2
            ) if monthly_metrics["orders"] > 0 else 0
        },
        "trend_7_days": data["last_7_days"]
    }
```

#### 8.4 Testing Analytics Endpoints

**Register routers:**
```python
from app.routers import (
    products, customers, orders, admin, reviews,
    vector_search, stores, analytics, dashboard
)

app.include_router(analytics.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
```

**Test endpoints:**
```
GET /api/v1/analytics/sales-summary?group_by=day
GET /api/v1/analytics/top-products?limit=10
GET /api/v1/analytics/customer-segmentation
GET /api/v1/analytics/category-performance
GET /api/v1/dashboard/overview
```

#### 8.5 Hands-On Exercise: Build a Custom Report

**Goal**: Create a "Customer Lifetime Value" report that combines orders, products, and customer data.

**Requirements:**
1. Calculate total spent, average order value, purchase frequency
2. Segment by customer acquisition date (cohort analysis)
3. Predict customer churn risk based on days since last order
4. Use $lookup to enrich with customer details
5. Add filters for date range and minimum order count

**Bonus**: Export results as CSV or stream large reports!

---

### Summary: DocumentDB Superpowers Unlocked! 🎉

✅ **Vector Search**: AI-powered semantic search and recommendations  
✅ **Geospatial Queries**: Location-based features with PostGIS integration  
✅ **Advanced Aggregations**: Real-time analytics with multi-stage pipelines  
✅ **PostgreSQL Backend**: Enterprise performance and reliability  

**Next**: Part 4 - Production Ready (optimization, testing, deployment)!

