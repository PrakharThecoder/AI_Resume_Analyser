import httpx
import json
import time
from app.core.config import settings
from app.core.logger import llm_logger
from app.services.prompt_service import PromptEngineeringService
import app.core.http_client as hc
from app.core.metrics import metrics

async def check_ollama_connection() -> dict:
    """Check if the Ollama server is running and reachable."""
    import asyncio
    max_retries = 5
    base_delay = 2.0
    for attempt in range(max_retries):
        try:
            if hc.http_client is None:
                # Fallback if accessed before lifespan
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{settings.OLLAMA_BASE_URL}")
            else:
                response = await hc.http_client.get(f"{settings.OLLAMA_BASE_URL}", timeout=5.0)
                
            response.raise_for_status()
            llm_logger.info("Health check result: Ollama server is reachable and connected.")
            return {"status": "connected", "message": "Ollama server is reachable"}
        except Exception as e:
            if attempt < max_retries - 1:
                llm_logger.warning(f"Ollama connection attempt {attempt + 1} failed, retrying in {base_delay}s... Error: {e}")
                await asyncio.sleep(base_delay)
                base_delay *= 1.5
            else:
                llm_logger.error(f"Health check failed: Ollama connection failed after {max_retries} attempts: {e}")
                return {"status": "disconnected", "message": str(e)}

async def check_model_availability() -> dict:
    """Check if the required model is pulled and available."""
    try:
        if hc.http_client is None:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        else:
            response = await hc.http_client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            
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
        "stream": False,
        "keep_alive": 0
    }
    if system_prompt:
        payload["system"] = system_prompt
        
    llm_logger.info(f"Model name used: {settings.OLLAMA_MODEL}")
    llm_logger.info(f"Prompt sent: {prompt}")
    llm_logger.debug(f"Ollama request payload: {json.dumps(payload)}")
    
    try:
        if hc.http_client is None:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.post(url, json=payload)
        else:
            response = await hc.http_client.post(url, json=payload)
            
        response.raise_for_status()
        
        data = response.json()
        response_text = data.get("response", "")
        
        duration = time.time() - start_time
        metrics.add_inference_time(duration * 1000)
        llm_logger.info(f"Request success: Response generated in {duration:.2f}s ({duration*1000:.2f}ms)")
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

async def generate_ai_resume_analysis(resume_text: str, deterministic_stats: dict) -> dict:
    start_time = time.time()
    prompt = PromptEngineeringService.get_resume_insights_prompt(
        resume_text=resume_text,
        deterministic_stats=deterministic_stats
    )

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": 0
    }

    llm_logger.info("Request start: Generating AI resume insights from LLM")
    llm_logger.debug(f"Prompt sent to model: {prompt}")

    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        if hc.http_client is None:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.post(url, json=payload)
        else:
            response = await hc.http_client.post(url, json=payload)
            
        response.raise_for_status()
        data = response.json()
        response_text = data.get("response", "{}")
        
        duration = time.time() - start_time
        metrics.add_inference_time(duration * 1000)
        llm_logger.info(f"Request success: Response generated in {duration:.2f}s ({duration*1000:.2f}ms)")
        llm_logger.debug(f"Response received from model: {response_text}")
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            llm_logger.error(f"Parsing error: Failed to parse JSON response: {e}. Raw response: {response_text}")
            raise ValueError("LLM returned invalid JSON")
        
        return {
            "candidate_summary": result.get("candidate_summary", "No summary provided."),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "recommendations": result.get("recommendations", []),
            "interview_tips": result.get("interview_tips", [])
        }
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Ollama API error {e.response.status_code}: {e.response.text}"
        llm_logger.error(error_msg, exc_info=True)
        return {
            "candidate_summary": f"Error generating analysis: {error_msg}",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "interview_tips": []
        }
    except Exception as e:
        error_msg = f"Ollama execution error: {str(e)}"
        llm_logger.error(error_msg, exc_info=True)
        return {
            "candidate_summary": f"Error generating analysis: {error_msg}",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "interview_tips": []
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
        "format": "json",
        "keep_alive": 0
    }

    llm_logger.info("Request start: Generating interview questions from LLM")
    llm_logger.debug(f"User prompt: {user_prompt}")

    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        if hc.http_client is None:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.post(url, json=payload)
        else:
            response = await hc.http_client.post(url, json=payload)
            
        response.raise_for_status()
        data = response.json()
        response_text = data.get("response", "{}")
        
        duration = time.time() - start_time
        metrics.add_inference_time(duration * 1000)
        llm_logger.info(f"Request success: Questions generated in {duration:.2f}s ({duration*1000:.2f}ms)")
        
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
