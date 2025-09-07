from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

db = MongoDB()

async def connect_to_mongo():
    """Create database connection."""
    try:
        # Log connection attempt (without sensitive data)
        logger.info(f"Connecting to MongoDB...")
        
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        
        # Verify connection
        await db.client.admin.command('ping')
        
        db.database = db.client[settings.MONGODB_DATABASE]
        
        logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    if db.database is None:
        raise ValueError("Database not initialized. Please check MongoDB connection.")
    return db.database