import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"

# Upload #1
print("--- Uploading Resume #1 ---")
resp1 = client.post("/api/v1/resumes/upload-resume", files={"file": ("dummy.pdf", pdf_content, "application/pdf")})
print(resp1.json())
resume_id_1 = resp1.json()['resume_id']

# Parse #1 (Expected: MISS)
print("--- Parsing Resume #1 ---")
parse_resp1 = client.post(f"/api/v1/resumes/parse-resume/{resume_id_1}")
print("Parse Response 1 Status:", parse_resp1.status_code)

# Upload #2 (Identical Content)
print("\n--- Uploading Resume #2 (Identical Content) ---")
resp2 = client.post("/api/v1/resumes/upload-resume", files={"file": ("dummy.pdf", pdf_content, "application/pdf")})
resume_id_2 = resp2.json()['resume_id']

# Parse #2 (Expected: HIT)
print("--- Parsing Resume #2 ---")
parse_resp2 = client.post(f"/api/v1/resumes/parse-resume/{resume_id_2}")
print("Parse Response 2 Status:", parse_resp2.status_code)

# Check Cache Debug Endpoint
print("\n--- Cache Debug Stats ---")
debug_resp = client.get("/api/v1/cache/debug")
print(debug_resp.json())
