import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io
import os

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_resume_analyzer.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_teardown():
    # Setup: Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Teardown: Drop tables and remove file
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_resume_analyzer.db"):
        try:
            os.remove("./test_resume_analyzer.db")
        except PermissionError:
            pass

def test_upload_and_parse_resume(setup_teardown):
    # 1. Test uploading a resume
    # Create a dummy PDF content (note: PyPDF2/pdfplumber might fail on invalid PDF, 
    # but for endpoint testing we can pass a minimum valid PDF or test error handling.
    # We will use a minimal valid PDF byte string.
    minimal_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 53 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(John Doe Resume) Tj\nET\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000288 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n392\n%%EOF"
    )
    
    file_obj = io.BytesIO(minimal_pdf)
    file_obj.name = "test_resume.pdf"
    
    response = client.post(
        "/api/v1/resumes/upload-resume",
        files={"file": ("test_resume.pdf", file_obj, "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "resume_id" in data
    assert data["filename"] == "test_resume.pdf"
    assert data["upload_status"] == "success"
    
    resume_id = data["resume_id"]
    
    # 2. Test parsing the uploaded resume
    parse_response = client.post(f"/api/v1/resumes/parse-resume/{resume_id}")
    
    # Depending on how the dummy PDF is parsed, we might get 200 or an error if pdfplumber fails.
    # Since our fallback handles exceptions and might return empty fields, it should return 200.
    assert parse_response.status_code == 200
    parsed_data = parse_response.json()
    
    assert "name" in parsed_data
    assert "email" in parsed_data
    assert "phone" in parsed_data
    assert "skills" in parsed_data
    assert "education" in parsed_data
    assert "experience" in parsed_data
    assert "projects" in parsed_data
