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
    total_feedbacks: int
    team_performance: List[Dict]
    sentiment_analysis: Dict
    recommendations: List[str]
    analysis_timestamp: datetime
    
class TeamRanking(BaseModel):
    team_id: int
    score: float
    strengths: Optional[List[str]] = None
    issues: Optional[List[str]] = None
    improvement_suggestions: Optional[List[str]] = None

class TeamRankings(BaseModel):
    best_teams: List[TeamRanking]
    teams_needing_improvement: List[TeamRanking]

class Analysis(BaseModel):
    overall_summary: str
    team_rankings: TeamRankings

class AIAnalysisResponse(BaseModel):
    total_feedback_count: int
    teams_analyzed: int
    analysis: Analysis
    key_insights: List[str]
    recommendations: List[str]
    analyzed_at: datetime