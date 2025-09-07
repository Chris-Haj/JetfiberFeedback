import openai
import json
import logging
from typing import Dict, List
from datetime import datetime

from ..config import settings
from ..models import AIAnalysisResponse, Analysis, TeamRankings, TeamRanking

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
    
    async def comprehensive_analysis(self, feedbacks: List[dict]) -> AIAnalysisResponse:
        """Perform comprehensive AI analysis on all feedbacks."""
        try:
            # Prepare team performance data
            team_stats = {}
            
            for fb in feedbacks:
                team_id = fb["team_id"]
                answers = fb["answers"]
                
                if team_id not in team_stats:
                    team_stats[team_id] = {
                        "total": 0,
                        "on_time_yes": 0,
                        "recommend_yes": 0,
                        "installation_ratings": [],
                        "helpfulness_ratings": [],
                        "positive_feedback": [],
                        "negative_feedback": []
                    }
                
                stats = team_stats[team_id]
                stats["total"] += 1
                stats["on_time_yes"] += 1 if answers.get("on_time") is True else 0
                stats["recommend_yes"] += 1 if answers.get("recommend") is True else 0
                stats["installation_ratings"].append(answers.get("installation_rating", 0))
                stats["helpfulness_ratings"].append(answers.get("helpfulness_rating", 0))
                
                # Collect feedback text
                if answers.get("like_most"):
                    stats["positive_feedback"].append(answers["like_most"])
                if answers.get("improve"):
                    stats["negative_feedback"].append(answers["improve"])
            
            # Calculate team performance metrics
            team_performance = []
            for team_id, stats in team_stats.items():
                avg_installation = sum(stats["installation_ratings"]) / len(stats["installation_ratings"]) if stats["installation_ratings"] else 0
                avg_helpfulness = sum(stats["helpfulness_ratings"]) / len(stats["helpfulness_ratings"]) if stats["helpfulness_ratings"] else 0
                overall_score = (avg_installation + avg_helpfulness) / 2
                
                team_performance.append({
                    "team_id": team_id,
                    "total_feedbacks": stats["total"],
                    "overall_score": overall_score,
                    "on_time_percentage": (stats["on_time_yes"] / stats["total"] * 100) if stats["total"] > 0 else 0,
                    "recommend_percentage": (stats["recommend_yes"] / stats["total"] * 100) if stats["total"] > 0 else 0,
                    "positive_feedback": stats["positive_feedback"][:3],  # Top 3
                    "negative_feedback": stats["negative_feedback"][:3]   # Top 3
                })
            
            # Sort teams by score
            team_performance.sort(key=lambda x: x["overall_score"], reverse=True)
            
            # Create prompt for OpenAI
            analysis_prompt = f"""
            أنت محلل بيانات متخصص في تقييم أداء فرق تركيب الإنترنت. قم بتحليل البيانات التالية وقدم تقريرًا شاملاً باللغة العربية.

            عدد التقييمات الإجمالي: {len(feedbacks)}
            عدد الفرق: {len(team_stats)}
            
            بيانات أداء الفرق:
            {json.dumps(team_performance, ensure_ascii=False, indent=2)}
            
            المطلوب:
            قدم تحليلاً شاملاً يتضمن:
            1. ملخص عام عن أداء جميع الفرق
            2. تصنيف الفرق (أفضل الفرق والفرق التي تحتاج تحسين)
            3. رؤى رئيسية حول الأداء العام
            4. توصيات محددة للتحسين
            
            يجب أن تكون الإجابة بتنسيق JSON بالضبط كما يلي:
            {{
                "overall_summary": "ملخص شامل بالعربية",
                "best_teams": [
                    {{
                        "team_id": رقم_الفريق,
                        "score": النقاط,
                        "strengths": ["نقطة قوة 1", "نقطة قوة 2"]
                    }}
                ],
                "teams_needing_improvement": [
                    {{
                        "team_id": رقم_الفريق,
                        "issues": ["مشكلة 1", "مشكلة 2"],
                        "improvement_suggestions": ["اقتراح 1", "اقتراح 2"]
                    }}
                ],
                "key_insights": ["رؤية 1", "رؤية 2", "رؤية 3"],
                "recommendations": ["توصية 1", "توصية 2", "توصية 3"]
            }}
            """
            
            # Get AI analysis
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت محلل بيانات خبير يقدم تحليلات دقيقة باللغة العربية."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            # Build the response
            best_teams = []
            for team in ai_result.get("best_teams", []):
                best_teams.append(TeamRanking(**team))
            
            teams_needing_improvement = []
            for team in ai_result.get("teams_needing_improvement", []):
                teams_needing_improvement.append(TeamRanking(**team))
            
            analysis = Analysis(
                overall_summary=ai_result.get("overall_summary", ""),
                team_rankings=TeamRankings(
                    best_teams=best_teams,
                    teams_needing_improvement=teams_needing_improvement
                )
            )
            
            return AIAnalysisResponse(
                total_feedback_count=len(feedbacks),
                teams_analyzed=len(team_stats),
                analysis=analysis,
                key_insights=ai_result.get("key_insights", []),
                recommendations=ai_result.get("recommendations", []),
                analyzed_at=datetime.utcnow()
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            raise