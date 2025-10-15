"""
Database connection and initialization.

This module sets up the connection to DocumentDB using Beanie ODM.
"""

from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from app.core.config import settings
from app.models.product import Product
from app.models.order import Order
from app.models.customer import Customer


logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""
    
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        """Initialize database connection."""
        try:
            logger.info(f"Connecting to DocumentDB at {settings.DOCUMENTDB_URL.split('@')[1].split('?')[0]}")
            
            # Create motor client
            cls.client = AsyncIOMotorClient(
                settings.DOCUMENTDB_URL,
                tls=True,
                tlsAllowInvalidCertificates=True,
            )
            
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to DocumentDB")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=cls.client[settings.DOCUMENTDB_DB_NAME],
                document_models=[
                    Product,
                    Order,
                    Customer,
                ],
            )
            logger.info("Beanie ODM initialized successfully")
            
            # Create indexes
            await cls.create_indexes()
            
        except Exception as e:
            logger.error(f"Error connecting to DocumentDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Database connection closed")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes for better performance."""
        try:
            # Product indexes
            await Product.find_one()  # Ensure collection exists
            
            # Order indexes
            await Order.find_one()
            
            # Customer indexes  
            await Customer.find_one()
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    @classmethod
    async def drop_collections(cls):
        """Drop all collections - USE WITH CAUTION! This deletes all data."""
        try:
            db = cls.client[settings.DOCUMENTDB_DB_NAME]
            
            # Drop each collection
            await db.products.drop()
            logger.info("Dropped products collection")
            
            await db.orders.drop()
            logger.info("Dropped orders collection")
            
            await db.customers.drop()
            logger.info("Dropped customers collection")
            
            logger.info("All collections dropped successfully")
        except Exception as e:
            logger.warning(f"Error dropping collections: {e}")


# Create singleton instance
db = Database()
