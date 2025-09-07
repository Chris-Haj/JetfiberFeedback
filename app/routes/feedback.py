from fastapi import APIRouter, HTTPException, Query, Depends, Path
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
    """Create a new feedback entry."""
    try:
        result = await feedback_service.create_feedback(feedback, database)
        return result
    except Exception as e:
        logger.error(f"Error in create_feedback endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[FeedbackResponse])
async def get_all_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    database=Depends(get_database)
):
    """Get all feedbacks with pagination."""
    try:
        feedbacks = await feedback_service.get_feedbacks(
            database=database,
            skip=skip,
            limit=limit
        )
        return feedbacks
    except Exception as e:
        logger.error(f"Error in get_all_feedbacks endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_by_id(
    feedback_id: str = Path(..., description="The ID of the feedback to retrieve"),
    database=Depends(get_database)
):
    """Get a specific feedback by its ID."""
    try:
        feedback = await feedback_service.get_feedback_by_id(
            database=database,
            feedback_id=feedback_id
        )
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return feedback
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_feedback_by_id endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))