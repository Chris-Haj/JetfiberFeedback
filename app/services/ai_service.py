import json
import logging
from typing import Dict, List
from datetime import datetime
from openai import AsyncOpenAI

from ..config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
    
    async def comprehensive_analysis(self, feedbacks: List[dict]) -> Dict:
        """Perform comprehensive AI analysis on all feedbacks."""
        try:
            # Count unique teams
            unique_teams = len(set(fb.get("team_id") for fb in feedbacks if fb.get("team_id")))
            
            # Prepare feedback data for AI
            feedback_data = []
            for fb in feedbacks:
                feedback_data.append({
                    "team_id": fb.get("team_id"),
                    "answers": fb.get("answers", {})
                })
            
            # Create prompt for OpenAI
            analysis_prompt = f"""
أنت محلل بيانات متخصص في تقييم أداء فرق تركيب الإنترنت. قم بتحليل البيانات التالية وقدم تقريرًا شاملاً باللغة العربية.

بيانات التقييمات ({len(feedbacks)} تقييم):
{json.dumps(feedback_data, ensure_ascii=False, indent=2)}

قدم التحليل بالتنسيق JSON التالي بالضبط:
{{
    "analysis": {{
        "overall_summary": "ملخص شامل عن أداء جميع الفرق",
        "team_rankings": {{
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
            ]
        }}
    }},
    "key_insights": ["رؤية رئيسية 1", "رؤية رئيسية 2", "رؤية رئيسية 3"],
    "recommendations": ["توصية 1", "توصية 2", "توصية 3", "توصية 4", "توصية 5"]
}}

ملاحظة: يجب أن تكون جميع النصوص باللغة العربية.
"""
            
            # Get AI analysis using new OpenAI syntax
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت محلل بيانات خبير يقدم تحليلات دقيقة باللغة العربية في تنسيق JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            # Build the final response
            return {
                "total_feedback_count": len(feedbacks),
                "teams_analyzed": unique_teams,
                "analysis": ai_result.get("analysis", {}),
                "key_insights": ai_result.get("key_insights", []),
                "recommendations": ai_result.get("recommendations", []),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            raise