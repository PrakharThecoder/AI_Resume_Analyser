import httpx

# Global HTTP client for connection pooling
http_client: httpx.AsyncClient = None
