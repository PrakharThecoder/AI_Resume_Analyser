import logging
import re
import json

logger = logging.getLogger(__name__)

class ATSScorerService:
    def __init__(self):
        # Weights
        self.weights = {
            "skills": 50,
            "experience": 20,
            "education": 15,
            "projects": 10,
            "certifications": 5
        }

    def score(self, resume_content: str, parsed_resume: dict, parsed_jd: dict) -> dict:
        """
        Calculates ATS score deterministically without LLMs.
        """
        # 1. Skill Match (50%)
        req_skills = parsed_jd.get("required_skills", [])
        pref_skills = parsed_jd.get("preferred_skills", [])
        all_jd_skills = [s.lower() for s in req_skills + pref_skills]
        
        logger.info(f"JD skills extracted: {all_jd_skills}")
        
        resume_skills_section = parsed_resume.get("skills", [])
        resume_skills_lower = [s.lower() for s in resume_skills_section] if resume_skills_section else []
        logger.info(f"Resume skills extracted: {resume_skills_lower}")
        
        # Also look in raw content if not found in skills list
        content_lower = resume_content.lower() if resume_content else ""
        
        matched_skills = []
        missing_skills = []
        
        for s in all_jd_skills:
            # check exact match in list or word match in content
            if s in resume_skills_lower or re.search(r'\b' + re.escape(s) + r'\b', content_lower):
                matched_skills.append(s)
            else:
                missing_skills.append(s)
                
        logger.info(f"Matched skills: {matched_skills}")
        logger.info(f"Missing skills: {missing_skills}")
                
        if all_jd_skills and matched_skills:
            skill_score_ratio = len(matched_skills) / len(all_jd_skills)
        else:
            skill_score_ratio = 0.0 # If no matched skills exist, score is 0
            
        skill_score = skill_score_ratio * self.weights["skills"]

        # 2. Experience Match (20%)
        exp_req = parsed_jd.get("experience_requirement", "").lower()
        resume_exp = parsed_resume.get("experience", [])
        resume_exp_str = " ".join(resume_exp).lower() if resume_exp else content_lower
        
        exp_score = self._evaluate_experience(exp_req, resume_exp_str) * self.weights["experience"]

        # 3. Education Match (15%)
        edu_req = parsed_jd.get("education_requirement", "").lower()
        resume_edu = parsed_resume.get("education", [])
        resume_edu_str = " ".join(resume_edu).lower() if resume_edu else content_lower
        
        edu_score = self._evaluate_education(edu_req, resume_edu_str) * self.weights["education"]

        # 4. Projects Match (10%)
        projects = parsed_resume.get("projects", [])
        projects_score = self.weights["projects"] if projects and len(projects) > 0 else 0.0

        # 5. Certifications Match (5%)
        cert_score = self._evaluate_certifications(content_lower) * self.weights["certifications"]

        # Overall Calculation
        total_score = skill_score + exp_score + edu_score + projects_score + cert_score

        logger.info(f"Final ATS score: {total_score}")

        recommendations = []
        if missing_skills:
            recommendations.append(f"Consider adding missing keywords like: {', '.join(missing_skills[:3])}")
        if exp_score < self.weights["experience"]:
            recommendations.append("Ensure your years of experience are clearly stated.")
        if edu_score < self.weights["education"]:
            recommendations.append("Make sure your education degrees match the JD requirements.")
        if projects_score == 0:
            recommendations.append("Add a projects section to highlight your hands-on work.")
        if cert_score == 0:
            recommendations.append("If you have relevant certifications, explicitly list them.")

        return {
            "ats_score": round(total_score, 1),
            "skill_match_score": round(skill_score, 1),
            "experience_score": round(exp_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations
        }

    def _evaluate_experience(self, exp_req: str, resume_exp_str: str) -> float:
        if not exp_req:
            return 0.0 # Do not assign default full marks
        
        # Simple heuristic: try to find years of exp required
        match = re.search(r'(\d+)[+\s]*years?', exp_req)
        if match:
            req_years = int(match.group(1))
            # try to find years in resume
            resume_years = re.findall(r'(\d+)[+\s]*years?', resume_exp_str)
            if resume_years:
                max_years = max([int(y) for y in resume_years])
                if max_years >= req_years:
                    return 1.0
                else:
                    return max_years / req_years
        
        # If no explicit numbers, but experience is required, just check if they have any
        if len(resume_exp_str) > 50:
            return 1.0
            
        return 0.0

    def _evaluate_education(self, edu_req: str, resume_edu_str: str) -> float:
        if not edu_req:
            return 0.0 # Do not assign default full marks
            
        degrees = {
            "bachelor": ["bachelor", "b.s", "bs", "b.a", "ba", "undergraduate"],
            "master": ["master", "m.s", "ms", "m.a", "ma", "graduate"],
            "phd": ["phd", "ph.d", "doctorate"]
        }
        
        for deg_type, keywords in degrees.items():
            # If JD mentions this degree
            if any(kw in edu_req for kw in keywords):
                # If resume also has this degree or higher
                if any(kw in resume_edu_str for kw in keywords):
                    return 1.0
        
        # If we can't find specific degree match, but they have education
        if len(resume_edu_str) > 20:
            return 0.5
            
        return 0.0

    def _evaluate_certifications(self, content_lower: str) -> float:
        cert_keywords = ["certification", "certified", "cpa", "aws", "azure", "gcp", "pmp", "cissp"]
        if any(kw in content_lower for kw in cert_keywords):
            return 1.0
        return 0.0
