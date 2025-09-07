from typing import List, Optional
from datetime import datetime
import logging
from bson import ObjectId

from ..models import FeedbackCreate, FeedbackResponse
from ..database import get_database
from ..config import settings

logger = logging.getLogger(__name__)

class FeedbackService:
    
    @staticmethod
    def feedback_helper(feedback) -> dict:
        """Convert MongoDB document to response model."""
        return {
            "id": str(feedback["_id"]),
            "team_id": feedback["team_id"],
            "answers": feedback["answers"],
            "created_at": feedback["created_at"]
        }
    
    async def create_feedback(self, feedback: FeedbackCreate, database) -> FeedbackResponse:
        """Create a new feedback entry."""
        try:
            # Convert to dict and add metadata
            feedback_dict = feedback.dict()
            feedback_dict["created_at"] = datetime.utcnow()
            
            # Insert into MongoDB
            collection = database[settings.COLLECTION_NAME]
            result = await collection.insert_one(feedback_dict)
            
            # Retrieve the created feedback
            created_feedback = await collection.find_one({"_id": result.inserted_id})
            
            return self.feedback_helper(created_feedback)
            
        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            raise
    
    async def get_feedbacks(
        self, 
        database,
        skip: int = 0,
        limit: int = 100
    ) -> List[FeedbackResponse]:
        """Get all feedbacks with pagination."""
        try:
            collection = database[settings.COLLECTION_NAME]
            
            # Execute query with pagination
            cursor = collection.find({}).skip(skip).limit(limit).sort("created_at", -1)
            feedbacks = await cursor.to_list(length=limit)
            print(feedbacks)
            
            return [self.feedback_helper(feedback) for feedback in feedbacks]
            
        except Exception as e:
            logger.error(f"Error fetching feedbacks: {e}")
            raise
    
    async def get_feedback_by_id(self, database, feedback_id: str) -> Optional[FeedbackResponse]:
        """Get a specific feedback by its ID."""
        try:
            collection = database[settings.COLLECTION_NAME]
            
            # Validate ObjectId format
            if not ObjectId.is_valid(feedback_id):
                logger.warning(f"Invalid ObjectId format: {feedback_id}")
                return None
            
            # Find the feedback
            feedback = await collection.find_one({"_id": ObjectId(feedback_id)})
            
            if feedback:
                return self.feedback_helper(feedback)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching feedback by ID: {e}")
            raise
    
    async def get_all_feedbacks(self, database) -> List[dict]:
        """Get all feedbacks for analysis (no filtering, returns raw data)."""
        try:
            collection = database[settings.COLLECTION_NAME]
            cursor = collection.find({})
            feedbacks = await cursor.to_list(length=None)
            return feedbacks
        except Exception as e:
            logger.error(f"Error fetching all feedbacks: {e}")
            raise