import logging

logger = logging.getLogger(__name__)

class DashboardService:
    @staticmethod
    async def get_dashboard_data() -> dict:
        """
        Retrieves dashboard data. 
        Currently returning a mocked payload based on user requirements.
        """
        logger.info("DashboardService: Fetching dashboard data")
        
        try:
            return {
                "ats_score": 82,
                "skill_match_percentage": 75,
                "matched_skills": [
                    "Python",
                    "FastAPI",
                    "React",
                    "SQL"
                ],
                "missing_skills": [
                    "Docker",
                    "AWS",
                    "Kubernetes"
                ],
                "resume_sections": {
                    "skills": 90,
                    "experience": 80,
                    "education": 85,
                    "projects": 70
                },
                "candidate_summary": "Strong backend developer",
                "strengths": [
                    "Backend Development",
                    "Database Design"
                ],
                "weaknesses": [
                    "Cloud Skills"
                ]
            }
        except Exception as e:
            logger.error(f"DashboardService: Error fetching data - {str(e)}", exc_info=True)
            raise e
