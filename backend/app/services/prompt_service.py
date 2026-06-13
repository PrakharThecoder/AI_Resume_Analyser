import json

class PromptEngineeringService:
    @staticmethod
    def get_resume_insights_prompt(resume_text: str, deterministic_stats: dict) -> str:
        return f"""
You are an expert ATS and recruitment AI. Based on the following deterministic ATS scores and the user's resume, generate professional insights.
DO NOT invent new scores. Only provide the requested text.

Deterministic Stats:
{json.dumps(deterministic_stats, indent=2)}

Resume Content:
{resume_text[:3000]}

Generate a JSON response EXACTLY matching this schema:
{{
    "candidate_summary": "Generate a professional 3-4 sentence summary of the candidate's resume strengths and readiness based on the ATS analysis.",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
    "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3", "Recommendation 4", "Recommendation 5"],
    "interview_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Only output valid JSON. Do not include markdown formatting or extra text.
"""
