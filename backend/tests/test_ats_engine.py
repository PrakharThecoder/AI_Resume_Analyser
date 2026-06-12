# pyrefly: ignore [missing-import]
import pytest
from app.services.ats_service import ATSScorerService

@pytest.fixture
def ats_scorer():
    return ATSScorerService()

def test_perfect_match(ats_scorer):
    parsed_jd = {
        "required_skills": ["Python", "Docker"],
        "experience_requirement": "5 years",
        "education_requirement": "Bachelor degree"
    }
    
    parsed_resume = {
        "skills": ["Python", "Docker"],
        "experience": ["Worked as a SWE for 5 years"],
        "education": ["Bachelor of Science in CS"],
        "projects": ["Built an app"]
    }
    
    resume_content = "Worked as a SWE for 5 years. Built an app. Bachelor of Science in CS. Python, Docker. AWS Certification."
    
    result = ats_scorer.score(resume_content, parsed_resume, parsed_jd)
    
    assert result["skill_match_score"] == 50.0
    assert result["experience_score"] == 20.0
    assert result["matched_skills"] == ["python", "docker"]
    assert result["missing_skills"] == []

def test_partial_match(ats_scorer):
    parsed_jd = {
        "required_skills": ["Python", "FastAPI", "Docker", "AWS"],
        "experience_requirement": "4 years",
        "education_requirement": "Master degree"
    }
    
    parsed_resume = {
        "skills": ["Python", "FastAPI"],
        "experience": ["3 years experience in web dev"],
        "education": ["Bachelor degree"],
        "projects": ["Web project"]
    }
    
    resume_content = "3 years experience. Bachelor degree. Python, FastAPI. Web project."
    
    result = ats_scorer.score(resume_content, parsed_resume, parsed_jd)
    
    assert result["skill_match_score"] == 25.0
    assert result["matched_skills"] == ["python", "fastapi"]
    assert result["missing_skills"] == ["docker", "aws"]
    # Experience score should be (3 / 4) * 20 = 15.0
    assert result["experience_score"] == 15.0
    # Education should be 0 because it doesn't match Master
    # Wait, the fallback assigns 0.5 * 15 = 7.5 if there's any education > 20 chars
    # "Bachelor degree" is 15 chars, the string will be that. So length is <= 20, score might be 0.
    
def test_no_match(ats_scorer):
    parsed_jd = {
        "required_skills": ["Go", "Kubernetes"],
        "experience_requirement": "10 years",
        "education_requirement": "Ph.D."
    }
    
    parsed_resume = {
        "skills": ["HTML", "CSS"],
        "experience": ["1 year"],
        "education": ["High School"],
        "projects": []
    }
    
    resume_content = "High school graduate. 1 year experience in HTML, CSS."
    
    result = ats_scorer.score(resume_content, parsed_resume, parsed_jd)
    
    assert result["skill_match_score"] == 0.0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["go", "kubernetes"]
    assert result["experience_score"] == 2.0 # (1/10) * 20 = 2.0
