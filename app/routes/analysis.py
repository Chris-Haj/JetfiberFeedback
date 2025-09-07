from fastapi import APIRouter, HTTPException, Depends
import logging

from ..models import AIAnalysisResponse
from ..database import get_database
from ..services import FeedbackService, AIService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analysis"])

feedback_service = FeedbackService()
ai_service = AIService()

@router.get("/ai_analysis", response_model=AIAnalysisResponse)
async def get_ai_analysis(database=Depends(get_database)):
    """Send all feedback data to OpenAI for comprehensive analysis."""
    try:
        # Get all feedbacks
        feedbacks = await feedback_service.get_all_feedbacks(database)
        
        if not feedbacks:
            raise HTTPException(status_code=404, detail="No feedbacks found")
        
        # Perform comprehensive AI analysis
        analysis_result = await ai_service.comprehensive_analysis(feedbacks)
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ai_analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))