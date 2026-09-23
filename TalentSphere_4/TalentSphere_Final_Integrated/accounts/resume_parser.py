"""Basic resume extraction for Milestone 2.

PDF and DOCX text is extracted when the corresponding libraries are installed.
The parser then uses lightweight NLP/regex rules to identify common skills,
experience and project sections. It intentionally avoids making the profile
dependent on an external NLP model.
"""

import re
from pathlib import Path


# Kept as a public alias for backward compatibility. The shared catalog is
# used so resume and job-description extraction produce the same canonical
# skill names.
from matching.skill_catalog import CANONICAL_SKILLS, extract_skills as _extract_catalog_skills

COMMON_SKILLS = CANONICAL_SKILLS



def extract_text_from_file(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return ""
        try:
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""

    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            return ""
        try:
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""

    return ""


def extract_skills(text):
    """Extract canonical skills using the shared skill taxonomy."""
    return _extract_catalog_skills(text)


def extract_experience_years(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            try:
                return min(float(match.group(1)), 50)
            except ValueError:
                pass
    return None


def extract_projects(text):
    match = re.search(
        r"(?:projects?|academic projects?|personal projects?)\s*[:\-]?\s*(.*?)(?=\n\s*(?:experience|education|skills|certifications?|achievements?|languages?)\s*[:\-]?\s*\n?|\Z)",
        text,
        re.I | re.S,
    )
    if not match:
        return ""
    value = re.sub(r"\n{3,}", "\n\n", match.group(1)).strip()
    return value[:5000]


def parse_resume(file_path):
    text = extract_text_from_file(file_path)
    if not text:
        return {"text": "", "skills": [], "experience_years": None, "projects": ""}

    return {
        "text": text,
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "projects": extract_projects(text),
    }


def apply_extracted_profile_data(profile, file_path):
    data = parse_resume(file_path)

    if data["skills"]:
        existing = profile.skills_list()
        merged = []
        seen = set()
        for skill in existing + data["skills"]:
            key = skill.strip().lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(skill.strip())
        profile.skills = ", ".join(merged)

    if data["experience_years"] is not None and float(profile.experience_years or 0) == 0:
        profile.experience_years = data["experience_years"]

    if data["projects"] and not profile.projects.strip():
        profile.projects = data["projects"]

    profile.save()
    return data
