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