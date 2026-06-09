# pyrefly: ignore [missing-import]
import pdfplumber
# pyrefly: ignore [missing-import]
import PyPDF2
import re
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ResumeParserService:
    def __init__(self):
        pass
        
    def parse(self, file_path: str) -> dict:
        logger.info(f"Starting parsing for {file_path}")
        try:
            text = self._extract_text(file_path)
            
            parsed_data = {
                "name": self._extract_name(text),
                "email": self._extract_email(text),
                "phone": self._extract_phone(text),
                "skills": self._extract_section(text, "skills"),
                "education": self._extract_section(text, "education"),
                "experience": self._extract_section(text, "experience"),
                "projects": self._extract_section(text, "projects")
            }
            logger.info("Successfully parsed resume data")
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {str(e)}")
            raise

    def _extract_text(self, file_path: str) -> str:
        text = ""
        # Use pdfplumber for better text extraction layout
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {str(e)}. Falling back to PyPDF2.")
            # Fallback to PyPDF2
            try:
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as inner_e:
                logger.error(f"Error extracting text with PyPDF2: {inner_e}")
                raise Exception("Failed to extract text from PDF")
        return text

    def _extract_name(self, text: str) -> str:
        # Basic heuristic: The first non-empty line is often the name
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            return lines[0][:100]  # Return first line up to 100 chars
        return ""

    def _extract_email(self, text: str) -> str:
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_regex, text)
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        # Regex to match common phone formats
        phone_regex = r'(\+\d{1,3}[-.\s]??\d{1,4}[-.\s]??\d{1,4}[-.\s]??\d{1,9})|(\(?\d{3}\)?[-.\s]??\d{3}[-.\s]??\d{4})'
        match = re.search(phone_regex, text)
        if match:
            # Clean up the matched string a bit
            return "".join([c for c in match.group(0) if c.isdigit() or c in "+-(). "]).strip()
        return ""

    def _extract_section(self, text: str, section_name: str) -> list[str]:
        # Very basic section extraction returning a list of strings
        # Look for the section heading, then capture until the next double newline or next heading
        lines = text.split('\n')
        in_section = False
        section_text = []
        
        # Common section headers
        keywords = {
            "skills": ["skills", "technical skills", "core competencies"],
            "education": ["education", "academic background", "qualifications"],
            "experience": ["experience", "work experience", "employment history", "professional experience"],
            "projects": ["projects", "personal projects", "academic projects"]
        }
        
        target_keywords = keywords.get(section_name.lower(), [section_name.lower()])
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check if we hit the start of our target section
            if not in_section:
                if any(line_lower == kw or line_lower.startswith(kw + ":") for kw in target_keywords):
                    in_section = True
                    continue
            
            if in_section:
                # If we hit an empty line that might be a section break, or another keyword
                is_other_heading = False
                if len(line.strip().split()) <= 4 and line.strip() != "":
                    for _, kws in keywords.items():
                        if any(line_lower == kw or line_lower.startswith(kw + ":") for kw in kws):
                            is_other_heading = True
                            break
                
                if is_other_heading:
                    break
                    
                if line.strip():
                    section_text.append(line.strip())
                
        # Basic parsing: split by bullet points or return as a list of lines
        result = []
        for line in section_text:
            # If line starts with a bullet point character
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                result.append(line.lstrip('•-* ').strip())
            else:
                result.append(line)
        return result
