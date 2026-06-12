import json

class PromptEngineeringService:
    @staticmethod
    def get_resume_analysis_prompt(parsed_resume: dict, parsed_jd: dict, ats_score: float) -> str:
        return f"""
You are an expert technical recruiter.
Analyze candidate resumes and compare them with job descriptions.

Provide:
- Objective feedback
- Missing skills
- Improvement recommendations
- Interview preparation advice

Keep output concise and professional.

Job Description:
{json.dumps(parsed_jd, indent=2)}

Parsed Resume:
{json.dumps(parsed_resume, indent=2)}
The candidate has an ATS match score of {ats_score}%.

Provide your detailed analysis as a JSON object with exactly these keys:
- "objective_feedback": A brief concise summary of the candidate's fit.
- "missing_skills": A list of strings of critical skills missing.
- "improvement_recommendations": A list of strings with actionable advice to improve the resume.
- "interview_preparation_advice": A list of strings with tips for interview preparation based on their profile and the JD.

Only output valid JSON. Do not include markdown formatting or extra text.
"""
