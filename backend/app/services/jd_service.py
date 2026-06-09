import logging
import re

logger = logging.getLogger(__name__)

class JDParserService:
    def __init__(self):
        pass
        
    def parse_text(self, text: str) -> dict:
        import traceback
        logger.info("Received request for JD text parsing")
        try:
            logger.info("Extracted job description text successfully")
            
            logger.info("Starting skills extraction step...")
            req_skills = self._extract_skills(text, "required_skills")
            pref_skills = self._extract_skills(text, "preferred_skills")
            
            logger.info("Starting experience extraction step...")
            exp_req = self._extract_string_requirement(text, "experience")
            edu_req = self._extract_string_requirement(text, "education")
            
            parsed_data = {
                "job_title": self._extract_job_title(text),
                "required_skills": req_skills,
                "preferred_skills": pref_skills,
                "experience_requirement": exp_req,
                "education_requirement": edu_req
            }
            logger.info("Successfully parsed JD data")
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing JD text: {str(e)}\n{traceback.format_exc()}")
            raise

    def _extract_job_title(self, text: str) -> str:
        # Simple heuristic: often the first non-empty line or explicitly labeled
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "Unknown Title"
        
        for line in lines[:5]:
            if line.lower().startswith("title:") or line.lower().startswith("job title:"):
                return line.split(":", 1)[1].strip()
        
        # Fallback to the first line
        return lines[0][:100]

    def _extract_skills(self, text: str, section_name: str) -> list[str]:
        if section_name == "preferred_skills":
            return [] # We put all skills in required_skills based on dictionary

        dictionary = {
            "Python": ["python"],
            "Java": ["java"],
            "JavaScript": ["javascript", "js"],
            "TypeScript": ["typescript", "ts"],
            "React": ["react", "react.js", "reactjs"],
            "Next.js": ["next.js", "nextjs", "next js"],
            "Node.js": ["node.js", "nodejs", "node"],
            "Express.js": ["express.js", "expressjs", "express"],
            "FastAPI": ["fastapi", "fast api"],
            "Django": ["django"],
            "Flask": ["flask"],
            "SQL": ["sql"],
            "MySQL": ["mysql"],
            "PostgreSQL": ["postgresql", "postgres"],
            "MongoDB": ["mongodb", "mongo"],
            "Docker": ["docker"],
            "Kubernetes": ["kubernetes", "k8s"],
            "AWS": ["aws", "amazon web services"],
            "Azure": ["azure"],
            "GCP": ["gcp", "google cloud platform", "google cloud"],
            "Git": ["git"],
            "Linux": ["linux"],
            "C": ["\\bc\\b"],
            "C++": ["c\\+\\+", "c plus plus"],
            "C#": ["c#", "c sharp"],
            "HTML": ["html", "html5"],
            "CSS": ["css", "css3"],
            "TailwindCSS": ["tailwindcss", "tailwind css", "tailwind"],
            "Machine Learning": ["machine learning", "ml"],
            "Deep Learning": ["deep learning", "dl"]
        }

        found_skills = set()
        text_lower = text.lower()
        
        # To avoid matching "c" in "machine", we use boundaries for single letters or specific terms
        # The dictionary aliases above are just strings, we'll compile them into regexes safely
        for skill_name, aliases in dictionary.items():
            for alias in aliases:
                # If alias already contains \b (like C), use it directly
                if '\\b' in alias:
                    pattern = alias
                else:
                    # Escape special characters except if it's already a regex string
                    # Actually aliases don't have special regex except what we explicitly wrote (like \+)
                    # Let's clean it up:
                    if '+' in alias and '\\+' not in alias:
                        pass # handled below
                    
                    safe_alias = alias.replace('+', '\\+').replace('.', '\\.')
                    pattern = r'\b' + safe_alias + r'\b'
                
                if re.search(pattern, text_lower):
                    found_skills.add(skill_name)
                    break # move to next skill if found

        return list(found_skills)

    def _extract_string_requirement(self, text: str, section_name: str) -> str:
        if section_name == "education":
            return self._extract_education(text)
            
        # Experience extraction
        text_lower = text.lower()
        # Look for e.g. "2 years experience", "3+ years", "minimum 1 year"
        pattern = r'(?:minimum\s+)?(\d+)(?:\+)?\s*years?(?:\s*of)?(?:\s*experience)?'
        matches = re.findall(pattern, text_lower)
        
        if matches:
            # Get the highest number mentioned
            years = max([int(m) for m in matches])
            return f"{years} years"
            
        return ""

    def _extract_education(self, text: str) -> str:
        lines = text.split('\n')
        keywords = ["education", "degree", "academic", "schooling"]
        extracted = []
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords) and len(line.split()) < 30:
                if any(char.isdigit() for char in line) or "degree" in line_lower or "bachelor" in line_lower or "master" in line_lower:
                    extracted.append(line.strip('•-* '))
        return " ".join(extracted[:2])
