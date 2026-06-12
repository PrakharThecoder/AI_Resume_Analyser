import httpx
import json
import time
from app.core.config import settings
from app.core.logger import llm_logger
from app.services.prompt_service import PromptEngineeringService

async def check_ollama_connection() -> dict:
    """Check if the Ollama server is running and reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}")
            response.raise_for_status()
            llm_logger.info("Health check result: Ollama server is reachable and connected.")
            return {"status": "connected", "message": "Ollama server is reachable"}
    except Exception as e:
        llm_logger.error(f"Health check failed: Ollama connection failed: {e}")
        return {"status": "disconnected", "message": str(e)}

async def check_model_availability() -> dict:
    """Check if the required model is pulled and available."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model.get("name") for model in data.get("models", [])]
            llm_logger.info(f"Configured model: {settings.OLLAMA_MODEL}")
            llm_logger.info(f"Available Ollama models: {', '.join(models)}")
            if settings.OLLAMA_MODEL in models:
                llm_logger.info(f"Model validation successful: {settings.OLLAMA_MODEL} is available.")
                return {"status": "available", "model": settings.OLLAMA_MODEL, "available_models": models}
            else:
                llm_logger.error(f"Model validation failed: {settings.OLLAMA_MODEL} not found among available models.")
                return {"status": "unavailable", "message": f"Model {settings.OLLAMA_MODEL} not found.", "available_models": models}
    except Exception as e:
        llm_logger.error(f"Failed to check model availability: {e}")
        return {"status": "error", "message": str(e)}

async def generate_response(prompt: str, system_prompt: str = None) -> str:
    """Generate a response using the local Ollama server."""
    start_time = time.time()
    
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    if system_prompt:
        payload["system"] = system_prompt
        
    llm_logger.info(f"Model name used: {settings.OLLAMA_MODEL}")
    llm_logger.info(f"Prompt sent: {prompt}")
    llm_logger.debug(f"Ollama request payload: {json.dumps(payload)}")
    
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            response_text = data.get("response", "")
            
            duration = time.time() - start_time
            llm_logger.info(f"Request success: Response generated in {duration:.2f}s")
            llm_logger.debug(f"Ollama response: {response_text}")
            
            if not response_text:
                raise ValueError("Empty response from model")
                
            return response_text
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Ollama API error {e.response.status_code}: {e.response.text}"
        llm_logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg)
        
    except Exception as e:
        error_msg = f"Ollama connection/execution error: {str(e)}"
        llm_logger.error(error_msg, exc_info=True)
        raise ConnectionError(error_msg)

async def generate_ai_resume_analysis(parsed_resume: dict, parsed_jd: dict, ats_score: float) -> dict:
    start_time = time.time()
    prompt = PromptEngineeringService.get_resume_analysis_prompt(
        parsed_resume=parsed_resume,
        parsed_jd=parsed_jd,
        ats_score=ats_score
    )

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    llm_logger.info("Request start: Generating AI resume analysis from LLM")
    llm_logger.debug(f"Prompt sent to model: {prompt}")

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "{}")
            
            duration = time.time() - start_time
            llm_logger.info(f"Request success: Response generated in {duration:.2f}s")
            llm_logger.debug(f"Response received from model: {response_text}")
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                llm_logger.error(f"Parsing error: Failed to parse JSON response: {e}. Raw response: {response_text}")
                raise ValueError("LLM returned invalid JSON")
            
            return {
                "objective_feedback": result.get("objective_feedback", "No feedback provided."),
                "missing_skills": result.get("missing_skills", []),
                "improvement_recommendations": result.get("improvement_recommendations", []),
                "interview_preparation_advice": result.get("interview_preparation_advice", [])
            }
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Ollama API error {e.response.status_code}: {e.response.text}"
        llm_logger.error(error_msg, exc_info=True)
        return {
            "objective_feedback": f"Error generating analysis: {error_msg}",
            "missing_skills": [],
            "improvement_recommendations": [],
            "interview_preparation_advice": []
        }
    except Exception as e:
        error_msg = f"Ollama execution error: {str(e)}"
        llm_logger.error(error_msg, exc_info=True)
        return {
            "objective_feedback": f"Error generating analysis: {error_msg}",
            "missing_skills": [],
            "improvement_recommendations": [],
            "interview_preparation_advice": []
        }

async def generate_interview_questions(resume_text: str, job_description: str) -> dict:
    from app.core.prompts import INTERVIEW_QUESTIONS_PROMPT
    start_time = time.time()
    
    user_prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}"
    
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": user_prompt,
        "system": INTERVIEW_QUESTIONS_PROMPT,
        "stream": False,
        "format": "json"
    }

    llm_logger.info("Request start: Generating interview questions from LLM")
    llm_logger.debug(f"User prompt: {user_prompt}")

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "{}")
            
            duration = time.time() - start_time
            llm_logger.info(f"Request success: Questions generated in {duration:.2f}s")
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                llm_logger.error(f"Parsing error: Failed to parse JSON response: {e}")
                raise ValueError("LLM returned invalid JSON")
                
            formatted_result = {
                "technical_questions": result.get("technical_questions", {"easy": [], "medium": [], "hard": []}),
                "project_questions": result.get("project_questions", {"easy": [], "medium": [], "hard": []}),
                "hr_questions": result.get("hr_questions", {"easy": [], "medium": [], "hard": []})
            }
            
            question_count = 0
            for category in formatted_result.values():
                for difficulty_list in category.values():
                    if isinstance(difficulty_list, list):
                        question_count += len(difficulty_list)
            
            llm_logger.info(f"Question count generated: {question_count}")
            
            return formatted_result
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Ollama API error {e.response.status_code}: {e.response.text}"
        llm_logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Ollama execution error: {str(e)}"
        llm_logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg)
