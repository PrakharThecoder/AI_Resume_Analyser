import httpx
import json
from app.core.config import settings

async def analyze_resume_with_llm(resume_text: str, job_description: str) -> dict:
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and technical recruiter.
    Analyze the following resume against the job description.
    
    Job Description:
    {job_description}
    
    Resume:
    {resume_text}
    
    Provide your analysis as a JSON object with exactly these keys:
    - "match_score": A number between 0 and 100 representing the percentage match.
    - "ats_feedback": A brief paragraph summarizing ATS compatibility, missing keywords, and formatting issues.
    - "llm_report": A detailed constructive feedback report for the candidate.
    
    Only output valid JSON. Do not include markdown formatting or extra text.
    """

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "{}")
            
            result = json.loads(response_text)
            
            return {
                "match_score": float(result.get("match_score", 0)),
                "ats_feedback": result.get("ats_feedback", "No ATS feedback provided."),
                "llm_report": result.get("llm_report", "No detailed report provided.")
            }
            
    except Exception as e:
        print(f"LLM Error: {e}")
        return {
            "match_score": 0.0,
            "ats_feedback": "Error communicating with local AI model.",
            "llm_report": str(e)
        }
