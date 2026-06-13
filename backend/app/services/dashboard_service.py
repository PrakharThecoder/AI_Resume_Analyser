import logging
from sqlalchemy.orm import Session
from app.db.models import Resume, ResumeAnalysis, ParsedResumeData

logger = logging.getLogger(__name__)

class DashboardService:
    @staticmethod
    async def get_dashboard_data(db: Session, user_id: int) -> dict:
        """
        Retrieves actual dashboard data based on the user's latest analysis or resume.
        """
        logger.info(f"DashboardService: Fetching dashboard data for user {user_id}")
        
        try:
            # 1. Try to get the latest full ResumeAnalysis
            latest_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == user_id).order_by(ResumeAnalysis.created_at.desc()).first()
            if latest_analysis:
                sections = latest_analysis.resume_sections or {}
                
                return {
                    "base_ats_score": latest_analysis.base_ats_score or 0,
                    "ats_score": latest_analysis.ats_score,
                    "skill_match_percentage": latest_analysis.skill_match_percentage or 0,
                    "matched_skills": latest_analysis.matched_skills or [],
                    "missing_skills": latest_analysis.missing_skills or [],
                    "section_scores": sections,
                    "candidate_summary": latest_analysis.candidate_summary or "Analysis complete.",
                    "strengths": latest_analysis.strengths or [],
                    "weaknesses": latest_analysis.weaknesses or [],
                    "recommendations": latest_analysis.recommendations or [],
                    "interview_tips": latest_analysis.interview_tips or []
                }
            
            # 2. No data available yet
            return {
                "base_ats_score": 0,
                "ats_score": None,
                "skill_match_percentage": 0,
                "matched_skills": [],
                "missing_skills": [],
                "section_scores": {
                    "skills": 0, "experience": 0, "education": 0, "formatting": 0, "readability": 0
                },
                "candidate_summary": "No resumes uploaded or analyzed yet. Upload a resume and run analysis to view your insights.",
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "interview_tips": []
            }
            
        except Exception as e:
            logger.error(f"DashboardService: Error fetching data for user {user_id} - {str(e)}", exc_info=True)
            raise e
