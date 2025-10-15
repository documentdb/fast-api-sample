"""
Admin utility endpoints for database management.
"""

from fastapi import APIRouter, HTTPException
from app.core.database import Database

router = APIRouter()


@router.post("/reset-database")
async def reset_database():
    """
    Drop all collections and recreate indexes.
    WARNING: This deletes ALL data in the database!
    """
    try:
        await Database.drop_collections()
        await Database.create_indexes()
        return {
            "message": "Database reset successful. All collections dropped and indexes recreated.",
            "warning": "All data has been deleted!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")
