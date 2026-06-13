import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- Running /api/v1/cache/test ---")
resp = client.post("/api/v1/cache/test")
print(resp.json())

print("\n--- Cache Debug Stats ---")
debug_resp = client.get("/api/v1/cache/debug")
print(debug_resp.json())
