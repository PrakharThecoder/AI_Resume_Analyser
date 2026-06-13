import re

BENCHMARKS = {
    "Software Engineer": ["Python", "Java", "JavaScript", "Git", "SQL", "Data Structures", "Algorithms", "REST APIs"],
    "Backend Developer": ["Python", "FastAPI", "Django", "Docker", "AWS", "SQL", "Git", "REST APIs"],
    "Frontend Developer": ["JavaScript", "React", "TypeScript", "Redux", "HTML", "CSS", "Git"],
    "Data Scientist": ["Python", "R", "SQL", "Machine Learning", "Pandas", "NumPy", "Statistics", "Data Visualization"],
    "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Docker", "AWS", "Machine Learning", "Deep Learning", "Algorithms"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Linux", "Bash", "CI/CD", "Terraform", "Git"]
}

class ATSScorerService:
    def __init__(self):
        pass

    def calculate_base_score(self, resume_content: str, parsed_resume: dict) -> dict:
        content_lower = resume_content.lower() if resume_content else ""

        # Contact Info (10%)
        has_email = bool(parsed_resume.get("email"))
        has_phone = bool(parsed_resume.get("phone"))
        contact_score = 10 if (has_email or has_phone) else 0

        # Education Section Quality (10%)
        edu = parsed_resume.get("education", [])
        edu_score = 10 if len(edu) > 0 else 0

        # Experience Section Quality (20%)
        exp = parsed_resume.get("experience", [])
        exp_score = 20 if len(exp) > 0 else 0

        # Skills Section Completeness (20%)
        skills = parsed_resume.get("skills", [])
        skills_score = min(len(skills) / 5.0, 1.0) * 20

        # ATS-Friendly Formatting (15%)
        format_score = (sum([bool(edu), bool(exp), bool(skills)]) / 3.0) * 15

        # Resume Length Appropriateness (10%)
        word_count = len(content_lower.split())
        if 300 <= word_count <= 1000:
            length_score = 10
        elif word_count < 300:
            length_score = (word_count / 300.0) * 10
        else:
            length_score = max(10 - ((word_count - 1000) / 200.0), 0)

        # Action Verbs Usage (10%)
        ACTION_VERBS = ["managed", "led", "developed", "designed", "created", "built", "implemented", "improved", "increased", "reduced", "delivered", "collaborated", "orchestrated", "engineered", "optimized"]
        verb_hits = sum(1 for verb in ACTION_VERBS if verb in content_lower)
        verbs_score = min(verb_hits / 5.0, 1.0) * 10

        # Readability Score (5%)
        sentences = re.split(r'[.!?]+', content_lower)
        sentences = [s for s in sentences if len(s.strip()) > 0]
        avg_words = word_count / len(sentences) if sentences else 0
        readability_score = 5 if 10 <= avg_words <= 20 else 2

        raw_score = contact_score + edu_score + exp_score + skills_score + format_score + length_score + verbs_score + readability_score
        
        # Normalize Score (Target Ranges: Poor 40-55, Average 60-75, Strong 75-85, Excellent 85-95)
        norm_score = max(40, min(95, raw_score * 0.95))

        return {
            "base_ats_score": round(norm_score),
            "section_scores": {
                "skills": round((skills_score/20)*100) if skills_score else 0,
                "education": round((edu_score/10)*100) if edu_score else 0,
                "experience": round((exp_score/20)*100) if exp_score else 0,
                "formatting": round((format_score/15)*100) if format_score else 0,
                "readability": round((readability_score/5)*100) if readability_score else 0
            }
        }

    def calculate_job_match_score(self, resume_content: str, parsed_resume: dict, parsed_jd: dict) -> dict:
        content_lower = resume_content.lower() if resume_content else ""

        req_skills = parsed_jd.get("required_skills", [])
        pref_skills = parsed_jd.get("preferred_skills", [])
        all_jd_skills = [s.lower() for s in req_skills + pref_skills]
        
        resume_skills_lower = [s.lower() for s in parsed_resume.get("skills", [])]
        
        matched_skills = []
        missing_skills = []
        
        for s in all_jd_skills:
            if s in resume_skills_lower or re.search(r'\b' + re.escape(s) + r'\b', content_lower):
                matched_skills.append(s.title())
            else:
                missing_skills.append(s.title())
                
        # Skill Match (50%)
        skill_match_percentage = int((len(matched_skills) / len(all_jd_skills)) * 100) if all_jd_skills else 100
        skill_score = (skill_match_percentage / 100.0) * 50

        # Experience Relevance (20%)
        exp_req = parsed_jd.get("experience_requirement", "").lower()
        resume_exp_str = " ".join(parsed_resume.get("experience", [])).lower()
        exp_match_ratio = self._evaluate_experience(exp_req, resume_exp_str)
        exp_score = exp_match_ratio * 20

        # Keyword Matching (15%)
        keyword_hits = sum(content_lower.count(s) for s in all_jd_skills)
        avg_mentions = keyword_hits / len(matched_skills) if matched_skills else 0
        keyword_score = min(avg_mentions / 2.0, 1.0) * 15

        # Education Match (5%)
        edu_req = parsed_jd.get("education_requirement", "").lower()
        resume_edu_str = " ".join(parsed_resume.get("education", [])).lower()
        edu_score = self._evaluate_education(edu_req, resume_edu_str) * 5

        # Project Relevance (10%)
        projects = parsed_resume.get("projects", [])
        proj_score = 10 if len(projects) > 0 else 0

        raw_score = skill_score + exp_score + keyword_score + edu_score + proj_score
        norm_score = max(40, min(95, raw_score * 0.95))

        return {
            "ats_score": round(norm_score),
            "skill_match_percentage": skill_match_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }
        
    def get_role_benchmark_skills(self, role: str, resume_content: str, parsed_resume: dict) -> dict:
        content_lower = resume_content.lower() if resume_content else ""
        benchmark = BENCHMARKS.get(role, BENCHMARKS["Software Engineer"])
        
        resume_skills_lower = [s.lower() for s in parsed_resume.get("skills", [])]
        
        matched_skills = []
        missing_skills = []
        
        for s in benchmark:
            if s.lower() in resume_skills_lower or re.search(r'\b' + re.escape(s.lower()) + r'\b', content_lower):
                matched_skills.append(s)
            else:
                missing_skills.append(s)
                
        skill_match_percentage = int((len(matched_skills) / len(benchmark)) * 100)
        return {
            "skill_match_percentage": skill_match_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }

    def _evaluate_experience(self, exp_req: str, resume_exp_str: str) -> float:
        if not exp_req:
            return 1.0
        match = re.search(r'(\d+)[+\s]*years?', exp_req)
        if match:
            req_years = int(match.group(1))
            resume_years = re.findall(r'(\d+)[+\s]*years?', resume_exp_str)
            if resume_years:
                max_years = max([int(y) for y in resume_years])
                if max_years >= req_years:
                    return 1.0
                else:
                    return max_years / req_years
        if len(resume_exp_str) > 50:
            return 1.0
        return 0.0

    def _evaluate_education(self, edu_req: str, resume_edu_str: str) -> float:
        if not edu_req:
            return 1.0
        degrees = {
            "bachelor": ["bachelor", "b.s", "bs", "b.a", "ba", "undergraduate"],
            "master": ["master", "m.s", "ms", "m.a", "ma", "graduate"],
            "phd": ["phd", "ph.d", "doctorate"]
        }
        for deg_type, keywords in degrees.items():
            if any(kw in edu_req for kw in keywords):
                if any(kw in resume_edu_str for kw in keywords):
                    return 1.0
        if len(resume_edu_str) > 20:
            return 0.5
        return 0.0
