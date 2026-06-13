import httpx
import logging
from typing import Optional
from app.core.config import settings
import app.core.http_client as hc

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.timeout = 30.0  # 30 seconds timeout

    async def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the local Ollama server.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": 0
        }
        
        try:
            if hc.http_client is None:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)
            else:
                # Use shared client, override timeout if necessary or just use default
                response = await hc.http_client.post(url, json=payload, timeout=self.timeout)
                
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "")
                
        except httpx.ReadTimeout:
            error_msg = f"Ollama generation timed out after {self.timeout}s for model {self.model}."
            logger.error(error_msg)
            raise TimeoutError(error_msg)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = f"Model '{self.model}' not found on Ollama server. Please ensure it is pulled."
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                error_msg = f"Ollama API returned an HTTP error: {e.response.status_code} - {e.response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Failed to connect to Ollama server at {self.base_url}: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

# Dependency for FastAPI
def get_ollama_service() -> OllamaService:
    return OllamaService()
