from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class AnswersModel(BaseModel):
    on_time: bool
    polite_professional: bool
    explained_service: bool
    left_clean: bool
    internet_speed_ok: bool
    installation_rating: int = Field(..., ge=1, le=5)
    helpfulness_rating: int = Field(..., ge=1, le=5)
    recommend: bool
    like_most: str = Field(..., min_length=1, max_length=1000)
    improve: str = Field(..., min_length=1, max_length=1000)
    additional_comments: Optional[str] = Field(None, max_length=1000)

class FeedbackCreate(BaseModel):
    team_id: int = Field(..., ge=1)
    answers: AnswersModel

class FeedbackResponse(BaseModel):
    id: str
    team_id: int
    answers: Dict
    created_at: datetime

class AIAnalysisResponse(BaseModel):
    total_feedback_count: int
    teams_analyzed: int
    analysis: Dict
    key_insights: List[str]
    recommendations: List[str]
    analyzed_at: str