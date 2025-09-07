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
            
            # Insert into MongoDB - FIXED: Using correct collection name
            collection = database[settings.COLLECTION_NAME]  # This will use "customer_feedback"
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
        team_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FeedbackResponse]:
        """Get feedbacks with optional team_id filter."""
        try:
            # FIXED: Using correct collection name
            collection = database[settings.COLLECTION_NAME]  # This will use "customer_feedback"
            
            # Build query
            query = {}
            if team_id is not None:
                query["team_id"] = team_id
            
            # Execute query
            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            feedbacks = await cursor.to_list(length=limit)
            
            return [self.feedback_helper(feedback) for feedback in feedbacks]
            
        except Exception as e:
            logger.error(f"Error fetching feedbacks: {e}")
            raise
    
    async def get_all_feedbacks(self, database) -> List[dict]:
        """Get all feedbacks for analysis."""
        try:
            # FIXED: Using correct collection name
            collection = database[settings.COLLECTION_NAME]  # This will use "customer_feedback"
            cursor = collection.find({})
            feedbacks = await cursor.to_list(length=None)
            return feedbacks
        except Exception as e:
            logger.error(f"Error fetching all feedbacks: {e}")
            raise