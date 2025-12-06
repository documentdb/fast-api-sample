# Module 03 - Advanced Querying and Filtering

[< Database Integration with Beanie ODM](Module-02.md) - [Production Ready: Testing and Deployment >](Module-04.md)

---

## Introduction

In this module, you'll learn advanced querying techniques to make your Reviews API more powerful and user-friendly. You'll implement features like calculating average ratings, filtering by multiple criteria, sorting by helpfulness, and searching review content.

These patterns are essential for production applications where users expect sophisticated search and filtering capabilities.

---

## Learning Objectives and Activities

- Build complex queries with multiple filters
- Implement aggregation pipelines for statistics
- Add full-text search capabilities
- Create compound sorting strategies
- Optimize queries for performance
- Calculate and cache aggregate data

---

## Module Exercises

1. Activity 1: Calculate Product Rating Statistics
2. Activity 2: Implement Advanced Filtering
3. Activity 3: Add Text Search to Reviews
4. Activity 4: Sort by Multiple Criteria
5. Activity 5: Optimize with Aggregation Pipelines

---

## Activity 1: Calculate Product Rating Statistics

One of the most important features for a review system is displaying aggregate statistics like average rating and total review count.

### Understanding Aggregation

MongoDB's aggregation framework allows you to:
- Group documents by field values
- Calculate statistics (average, sum, count)
- Filter and transform data in stages
- Perform complex computations

### Create a Statistics Endpoint

1. **Add a new endpoint to `backend/app/routers/reviews.py`**:

   ```python
   from typing import Dict, Any
   
   @router.get(
       "/products/{product_id}/statistics",
       response_model=Dict[str, Any],
       summary="Get review statistics for a product",
   )
   async def get_product_statistics(product_id: str) -> Dict[str, Any]:
       """
       Get aggregate statistics for a product's reviews.
       
       Returns:
       - **total_reviews**: Total number of reviews
       - **average_rating**: Average star rating
       - **rating_distribution**: Count of reviews per star rating (1-5)
       - **verified_purchase_percentage**: Percentage of verified purchases
       """
       # Verify product exists
       product = await Product.get(product_id)
       if not product:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Product with ID '{product_id}' not found",
           )
       
       # Get all active reviews for this product
       reviews = await Review.find(
           Review.product_id == product_id,
           Review.is_active == True
       ).to_list()
       
       if not reviews:
           return {
               "product_id": product_id,
               "total_reviews": 0,
               "average_rating": 0.0,
               "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
               "verified_purchase_percentage": 0.0,
           }
       
       # Calculate statistics
       total_reviews = len(reviews)
       total_rating = sum(review.rating for review in reviews)
       average_rating = round(total_rating / total_reviews, 2)
       
       # Rating distribution
       rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
       for review in reviews:
           rating_distribution[review.rating] += 1
       
       # Verified purchase percentage
       verified_count = sum(1 for review in reviews if review.verified_purchase)
       verified_percentage = round((verified_count / total_reviews) * 100, 2)
       
       return {
           "product_id": product_id,
           "total_reviews": total_reviews,
           "average_rating": average_rating,
           "rating_distribution": rating_distribution,
           "verified_purchase_percentage": verified_percentage,
           "most_helpful_review_id": max(reviews, key=lambda r: r.helpful_votes).id if reviews else None,
       }
   ```

2. **Test the statistics endpoint**:

   - Open Swagger UI (`/docs`)
   - Expand `GET /api/v1/reviews/products/{product_id}/statistics`
   - Enter a product ID that has reviews
   - Click "Execute"
   - Verify you get statistics like:
     ```json
     {
       "product_id": "507f1f77bcf86cd799439012",
       "total_reviews": 8,
       "average_rating": 4.25,
       "rating_distribution": {
         "1": 0,
         "2": 1,
         "3": 1,
         "4": 3,
         "5": 3
       },
       "verified_purchase_percentage": 75.00,
       "most_helpful_review_id": "507f1f77bcf86cd799439999"
     }
     ```

### Using Aggregation Pipelines

For better performance on large datasets, use MongoDB's aggregation pipeline:

1. **Create an optimized version**:

   ```python
   @router.get(
       "/products/{product_id}/statistics/aggregated",
       response_model=Dict[str, Any],
       summary="Get review statistics using aggregation pipeline",
   )
   async def get_product_statistics_aggregated(product_id: str) -> Dict[str, Any]:
       """
       Get aggregate statistics using MongoDB aggregation pipeline.
       More efficient for large datasets.
       """
       # Verify product exists
       product = await Product.get(product_id)
       if not product:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Product with ID '{product_id}' not found",
           )
       
       # Aggregation pipeline
       pipeline = [
           # Match reviews for this product
           {
               "$match": {
                   "product_id": product_id,
                   "is_active": True
               }
           },
           # Group and calculate statistics
           {
               "$group": {
                   "_id": "$product_id",
                   "total_reviews": {"$sum": 1},
                   "average_rating": {"$avg": "$rating"},
                   "verified_count": {
                       "$sum": {"$cond": ["$verified_purchase", 1, 0]}
                   },
                   "rating_1": {
                       "$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}
                   },
                   "rating_2": {
                       "$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}
                   },
                   "rating_3": {
                       "$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}
                   },
                   "rating_4": {
                       "$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}
                   },
                   "rating_5": {
                       "$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}
                   },
               }
           },
           # Project final shape
           {
               "$project": {
                   "product_id": "$_id",
                   "total_reviews": 1,
                   "average_rating": {"$round": ["$average_rating", 2]},
                   "rating_distribution": {
                       "1": "$rating_1",
                       "2": "$rating_2",
                       "3": "$rating_3",
                       "4": "$rating_4",
                       "5": "$rating_5"
                   },
                   "verified_purchase_percentage": {
                       "$round": [
                           {"$multiply": [
                               {"$divide": ["$verified_count", "$total_reviews"]},
                               100
                           ]},
                           2
                       ]
                   }
               }
           }
       ]
       
       # Execute aggregation
       result = await Review.get_motor_collection().aggregate(pipeline).to_list(1)
       
       if not result:
           return {
               "product_id": product_id,
               "total_reviews": 0,
               "average_rating": 0.0,
               "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
               "verified_purchase_percentage": 0.0,
           }
       
       return result[0]
   ```

### Performance Comparison

**Simple approach** (loading all documents):
- Easy to understand and implement
- Works well for < 1000 reviews per product
- Can be slow with large datasets

**Aggregation pipeline**:
- More complex but much faster
- Calculations happen in the database
- Recommended for production use
- Scales to millions of documents

---

## Activity 2: Implement Advanced Filtering

Let's enhance the review listing endpoint with more sophisticated filtering options.

### Add Advanced Filter Parameters

1. **Update the `list_reviews()` function**:

   ```python
   @router.get(
       "",
       response_model=ReviewListResponse,
       summary="List reviews with advanced filtering",
   )
   async def list_reviews(
       page: int = Query(1, ge=1, description="Page number"),
       page_size: int = Query(20, ge=1, le=100, description="Items per page"),
       product_id: Optional[str] = Query(None, description="Filter by product ID"),
       customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
       min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating"),
       max_rating: Optional[int] = Query(None, ge=1, le=5, description="Maximum rating"),
       verified_only: bool = Query(False, description="Only verified purchases"),
       min_helpful_votes: Optional[int] = Query(None, ge=0, description="Minimum helpful votes"),
       sort_by: str = Query("created_at", description="Sort field: created_at, rating, helpful_votes"),
       sort_order: str = Query("desc", description="Sort order: asc or desc"),
   ) -> ReviewListResponse:
       """
       Retrieve a paginated list of reviews with advanced filtering.
       
       Filters:
       - **product_id**: Get reviews for a specific product
       - **customer_id**: Get reviews by a specific customer
       - **min_rating** / **max_rating**: Filter by rating range
       - **verified_only**: Only show verified purchase reviews
       - **min_helpful_votes**: Minimum helpfulness threshold
       
       Sorting:
       - **sort_by**: Field to sort by (created_at, rating, helpful_votes)
       - **sort_order**: asc (ascending) or desc (descending)
       """
       # Build query
       query = Review.find(Review.is_active == True)
       
       # Apply filters
       if product_id:
           query = query.find(Review.product_id == product_id)
       
       if customer_id:
           query = query.find(Review.customer_id == customer_id)
       
       if min_rating is not None:
           query = query.find(Review.rating >= min_rating)
       
       if max_rating is not None:
           query = query.find(Review.rating <= max_rating)
       
       if verified_only:
           query = query.find(Review.verified_purchase == True)
       
       if min_helpful_votes is not None:
           query = query.find(Review.helpful_votes >= min_helpful_votes)
       
       # Apply sorting
       sort_field = getattr(Review, sort_by, Review.created_at)
       if sort_order == "desc":
           query = query.sort(-sort_field)
       else:
           query = query.sort(+sort_field)
       
       # Get total count
       total = await query.count()
       
       # Calculate pagination
       pages = ceil(total / page_size) if total > 0 else 0
       skip = (page - 1) * page_size
       
       # Fetch paginated results
       reviews = await query.skip(skip).limit(page_size).to_list()
       
       return ReviewListResponse(
           items=[ReviewResponse(**review.model_dump()) for review in reviews],
           total=total,
           page=page,
           page_size=page_size,
           pages=pages,
       )
   ```

2. **Test the advanced filters**:

   Try these filter combinations in Swagger UI:
   
   - **5-star reviews only**: `min_rating=5&max_rating=5`
   - **Verified purchases with high ratings**: `verified_only=true&min_rating=4`
   - **Most helpful reviews**: `sort_by=helpful_votes&sort_order=desc`
   - **Recent low ratings**: `max_rating=2&sort_by=created_at&sort_order=desc`

---

## Activity 3: Add Text Search to Reviews

Full-text search allows users to find reviews containing specific words or phrases.

### Create a Text Search Endpoint

1. **Add text search functionality**:

   ```python
   @router.get(
       "/search",
       response_model=ReviewListResponse,
       summary="Search reviews by text",
   )
   async def search_reviews(
       query: str = Query(..., min_length=3, description="Search query"),
       page: int = Query(1, ge=1, description="Page number"),
       page_size: int = Query(20, ge=1, le=100, description="Items per page"),
       product_id: Optional[str] = Query(None, description="Filter by product"),
   ) -> ReviewListResponse:
       """
       Search reviews by text in title and comment fields.
       
       Uses case-insensitive regex matching for flexible search.
       """
       # Build search query
       search_filter = {
           "$or": [
               {"title": {"$regex": query, "$options": "i"}},
               {"comment": {"$regex": query, "$options": "i"}},
           ]
       }
       
       # Start with active reviews
       find_query = Review.find(Review.is_active == True)
       
       # Add text search filter
       find_query = find_query.find(search_filter)
       
       # Optionally filter by product
       if product_id:
           find_query = find_query.find(Review.product_id == product_id)
       
       # Get total count
       total = await find_query.count()
       
       # Calculate pagination
       pages = ceil(total / page_size) if total > 0 else 0
       skip = (page - 1) * page_size
       
       # Fetch results sorted by relevance (helpful votes)
       reviews = await find_query.sort(-Review.helpful_votes).skip(skip).limit(page_size).to_list()
       
       return ReviewListResponse(
           items=[ReviewResponse(**review.model_dump()) for review in reviews],
           total=total,
           page=page,
           page_size=page_size,
           pages=pages,
       )
   ```

2. **Create a text index for better performance** (optional):

   In the Review model's Settings class, add:
   
   ```python
   class Settings:
       name = "reviews"
       indexes = [
           "product_id",
           "customer_id",
           "rating",
           "created_at",
           [("product_id", 1), ("rating", -1)],
           # Text index for search
           [("title", "text"), ("comment", "text")],  # Add this
       ]
   ```

3. **Test text search**:

   - Search for "excellent": Find reviews praising products
   - Search for "disappointed": Find negative feedback
   - Search for "battery": Find reviews mentioning battery life
   - Search for "shipping": Find delivery-related comments

### Advanced Search Features

For production applications, consider:

1. **Fuzzy matching** - Handle typos and similar words
2. **Search highlighting** - Show matching text in context
3. **Relevance scoring** - Rank results by match quality
4. **Autocomplete** - Suggest search terms as users type

---

## Activity 4: Sort by Multiple Criteria

Sometimes you need to sort by multiple fields, like "rating descending, then helpful votes descending".

### Implement Compound Sorting

1. **Add a compound sort endpoint**:

   ```python
   @router.get(
       "/products/{product_id}/reviews/sorted",
       response_model=ReviewListResponse,
       summary="Get product reviews with intelligent sorting",
   )
   async def get_product_reviews_sorted(
       product_id: str,
       page: int = Query(1, ge=1),
       page_size: int = Query(20, ge=1, le=100),
       sort_strategy: str = Query(
           "most_helpful",
           description="Sorting strategy: most_helpful, highest_rated, most_recent, lowest_rated"
       ),
   ) -> ReviewListResponse:
       """
       Get product reviews with predefined sorting strategies.
       
       Strategies:
       - **most_helpful**: Highest helpful votes, then highest rating
       - **highest_rated**: Highest rating, then most recent
       - **most_recent**: Newest first
       - **lowest_rated**: Lowest rating, then most recent (for critical feedback)
       """
       # Verify product exists
       product = await Product.get(product_id)
       if not product:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Product with ID '{product_id}' not found",
           )
       
       # Build base query
       query = Review.find(
           Review.product_id == product_id,
           Review.is_active == True
       )
       
       # Apply sorting strategy
       if sort_strategy == "most_helpful":
           # Sort by helpful_votes desc, then rating desc
           query = query.sort(-Review.helpful_votes, -Review.rating)
       
       elif sort_strategy == "highest_rated":
           # Sort by rating desc, then created_at desc
           query = query.sort(-Review.rating, -Review.created_at)
       
       elif sort_strategy == "most_recent":
           # Sort by created_at desc only
           query = query.sort(-Review.created_at)
       
       elif sort_strategy == "lowest_rated":
           # Sort by rating asc, then created_at desc
           query = query.sort(+Review.rating, -Review.created_at)
       
       else:
           raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail=f"Invalid sort strategy: {sort_strategy}",
           )
       
       # Get total count
       total = await query.count()
       
       # Calculate pagination
       pages = ceil(total / page_size) if total > 0 else 0
       skip = (page - 1) * page_size
       
       # Fetch paginated results
       reviews = await query.skip(skip).limit(page_size).to_list()
       
       return ReviewListResponse(
           items=[ReviewResponse(**review.model_dump()) for review in reviews],
           total=total,
           page=page,
           page_size=page_size,
           pages=pages,
       )
   ```

2. **Test different sorting strategies**:

   - **most_helpful**: Great for showing community favorites
   - **highest_rated**: Emphasize positive feedback
   - **most_recent**: Show latest opinions
   - **lowest_rated**: Prioritize critical feedback for improvement

---

## Activity 5: Optimize with Aggregation Pipelines

For complex queries combining filtering, sorting, and aggregation, use aggregation pipelines.

### Create a Comprehensive Review Summary

1. **Add an advanced summary endpoint**:

   ```python
   @router.get(
       "/products/{product_id}/summary",
       response_model=Dict[str, Any],
       summary="Get comprehensive review summary for a product",
   )
   async def get_product_review_summary(product_id: str) -> Dict[str, Any]:
       """
       Get a comprehensive summary of product reviews including:
       - Overall statistics
       - Recent reviews sample
       - Most helpful review
       - Rating trends
       """
       # Verify product exists
       product = await Product.get(product_id)
       if not product:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"Product with ID '{product_id}' not found",
           )
       
       # Get statistics
       statistics_pipeline = [
           {"$match": {"product_id": product_id, "is_active": True}},
           {
               "$group": {
                   "_id": None,
                   "total_reviews": {"$sum": 1},
                   "average_rating": {"$avg": "$rating"},
                   "total_helpful_votes": {"$sum": "$helpful_votes"},
               }
           }
       ]
       
       stats_result = await Review.get_motor_collection().aggregate(statistics_pipeline).to_list(1)
       
       if not stats_result:
           return {
               "product_id": product_id,
               "product_name": product.name,
               "statistics": {
                   "total_reviews": 0,
                   "average_rating": 0.0,
                   "total_helpful_votes": 0,
               },
               "recent_reviews": [],
               "most_helpful_review": None,
           }
       
       stats = stats_result[0]
       
       # Get recent reviews (last 5)
       recent_reviews = await Review.find(
           Review.product_id == product_id,
           Review.is_active == True
       ).sort(-Review.created_at).limit(5).to_list()
       
       # Get most helpful review
       most_helpful = await Review.find(
           Review.product_id == product_id,
           Review.is_active == True
       ).sort(-Review.helpful_votes).limit(1).to_list()
       
       return {
           "product_id": product_id,
           "product_name": product.name,
           "statistics": {
               "total_reviews": stats["total_reviews"],
               "average_rating": round(stats["average_rating"], 2),
               "total_helpful_votes": stats["total_helpful_votes"],
           },
           "recent_reviews": [
               {
                   "id": str(review.id),
                   "rating": review.rating,
                   "title": review.title,
                   "customer_name": review.customer_name,
                   "created_at": review.created_at.isoformat(),
               }
               for review in recent_reviews
           ],
           "most_helpful_review": {
               "id": str(most_helpful[0].id),
               "rating": most_helpful[0].rating,
               "title": most_helpful[0].title,
               "comment": most_helpful[0].comment,
               "helpful_votes": most_helpful[0].helpful_votes,
               "customer_name": most_helpful[0].customer_name,
           } if most_helpful else None,
       }
   ```

2. **Test the comprehensive summary**:

   - Open Swagger UI
   - Call `GET /api/v1/reviews/products/{product_id}/summary`
   - Verify you get all components of the summary
   - Check that the data makes sense

---

## Validation Checklist

Your advanced querying implementation is successful if:

- ✅ Product statistics endpoint calculates average ratings correctly
- ✅ Rating distribution shows counts for each star level
- ✅ Advanced filters work individually and in combination
- ✅ Text search finds reviews containing search terms
- ✅ Sorting strategies produce expected result order
- ✅ Compound sorting (multiple fields) works correctly
- ✅ Aggregation pipelines execute without errors
- ✅ Summary endpoint combines multiple data sources
- ✅ All endpoints handle edge cases (no reviews, invalid IDs)
- ✅ Performance is acceptable even with filters and sorting

---

## Common Issues and Troubleshooting

### Issue 1: Aggregation pipeline returns empty results

**Solution**:
- Check the `$match` stage filters are correct
- Verify field names match your model exactly
- Use `.get_motor_collection().aggregate()` for raw pipelines
- Test pipeline stages individually

### Issue 2: Text search is slow

**Solution**:
- Create a text index on `title` and `comment` fields
- Limit search to specific products when possible
- Consider using MongoDB Atlas Search for better performance
- Add pagination to limit result set size

### Issue 3: Compound sorting not working as expected

**Solution**:
- Check sort field order - first field is primary sort
- Verify field names are correct
- Use `-` prefix for descending, `+` for ascending
- Test with sample data that clearly shows sort order

---

## Success Criteria

To complete this module successfully, you should be able to:

- ✅ Calculate aggregate statistics using both simple and pipeline methods
- ✅ Implement advanced filtering with multiple criteria
- ✅ Add text search functionality to reviews
- ✅ Sort results by multiple fields with compound sorting
- ✅ Use aggregation pipelines for complex queries
- ✅ Optimize queries for performance
- ✅ Handle edge cases and errors gracefully
- ✅ Combine multiple query techniques in a single endpoint

---

## Next Steps

Proceed to [Module 4: Production Ready - Testing and Deployment](Module-04.md) to learn:

1. Writing comprehensive unit tests
2. Integration testing with pytest
3. Test fixtures and mocking
4. API documentation best practices
5. Deployment preparation and optimization

---

## Resources

- [MongoDB Aggregation Framework](https://www.mongodb.com/docs/manual/aggregation/)
- [Beanie Aggregation](https://beanie-odm.dev/tutorial/aggregation/)
- [MongoDB Query Operators](https://www.mongodb.com/docs/manual/reference/operator/query/)
- [MongoDB Text Search](https://www.mongodb.com/docs/manual/text-search/)
- [Query Optimization](https://www.mongodb.com/docs/manual/core/query-optimization/)
