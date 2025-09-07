from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from ..models import FeedbackCreate, FeedbackResponse
from ..database import get_database
from ..services import FeedbackService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])

feedback_service = FeedbackService()

@router.post("", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    feedback: FeedbackCreate,
    database=Depends(get_database)
):
    try:
        result = await feedback_service.create_feedback(feedback, database)
        return result
    except Exception as e:
        logger.error(f"Error in create_feedback endpoint: {e}")
     
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[FeedbackResponse])
async def get_feedbacks(
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    database=Depends(get_database)
):
    """Get feedbacks with optional team_id filter."""
    try:
        feedbacks = await feedback_service.get_feedbacks(
            database=database,
            team_id=team_id
        )
        return feedbacks
    except Exception as e:
        logger.error(f"Error in get_feedbacks endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))