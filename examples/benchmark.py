"""
Benchmark endpoints to demonstrate async performance benefits.

If using in walkthrough, add to backend/app/routers/
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