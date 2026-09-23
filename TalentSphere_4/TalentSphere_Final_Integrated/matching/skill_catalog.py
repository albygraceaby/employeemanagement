"""Shared skill taxonomy and normalization for TalentSphere.

This module is intentionally dependency-free so resume parsing, job parsing,
and matching all use the same canonical skill names.
"""

import re

# Alias -> canonical skill. Keep aliases lowercase.
SKILL_ALIASES = {
    "py": "python",
    "python3": "python",
    "python 3": "python",
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    "angular.js": "angular",
    "angularjs": "angular",
    "vue.js": "vue",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "k8s": "kubernetes",
    "kubernates": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "nlp": "nlp",
    "c++": "c++",
    "c#": "c#",
    "rest api": "rest api",
    "rest": "rest api",
}

# Canonical names are also searchable. Single-letter R is deliberately
# supported because it is a common programming language in job descriptions.
CANONICAL_SKILLS = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "r",
    "sql", "html", "css", "react", "angular", "vue", "django", "flask",
    "spring", "node.js", "php", "laravel", "mysql", "postgresql", "mongodb",
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "selenium", "manual testing", "software testing", "qa", "api testing",
    "postman", "rest api", "linux", "excel", "power bi", "tableau",
    "machine learning", "deep learning", "nlp", "data analysis", "pandas",
    "numpy", "communication", "problem solving", "artificial intelligence",
}

SEARCH_TERMS = sorted(
    set(CANONICAL_SKILLS) | set(SKILL_ALIASES),
    key=lambda value: (-len(value), value),
)

SKILL_CATEGORIES = {
    "Languages": {"python", "java", "javascript", "typescript", "c", "c++", "c#", "r", "php"},
    "Frontend": {"html", "css", "react", "angular", "vue"},
    "Backend": {"django", "flask", "spring", "node.js", "laravel", "rest api"},
    "Database": {"sql", "mysql", "postgresql", "mongodb"},
    "DevOps & Cloud": {"docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "linux"},
    "AI & Data": {"machine learning", "deep learning", "nlp", "data analysis", "pandas", "numpy", "artificial intelligence"},
    "QA & Testing": {"selenium", "manual testing", "software testing", "qa", "api testing", "postman"},
    "Analytics": {"excel", "power bi", "tableau"},
    "Soft Skills": {"communication", "problem solving"},
}

# Critical core skills carrying higher weight in missing skill analysis
CRITICAL_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "sql", "react", "django",
    "docker", "kubernetes", "aws", "machine learning", "postgresql", "node.js"
}


def normalize_skill(skill):
    """Return one canonical, lowercase skill name."""
    value = re.sub(r"\s+", " ", str(skill).strip().lower())
    return SKILL_ALIASES.get(value, value)


def normalize_skills(skills):
    return {normalize_skill(skill) for skill in (skills or []) if str(skill).strip()}


def get_skill_category(skill):
    """Return the domain category for a canonical skill."""
    norm = normalize_skill(skill)
    for category, skills in SKILL_CATEGORIES.items():
        if norm in skills:
            return category
    return "General Tech"


def get_skill_criticality(skill):
    """Return urgency/criticality level: 'Critical Core' vs 'Secondary'."""
    norm = normalize_skill(skill)
    if norm in CRITICAL_SKILLS:
        return "Critical Core"
    return "Secondary"


def _pattern(term):
    # Avoid substring false positives (e.g. "r" inside "react").
    return r"(?<![a-z0-9+#])" + re.escape(term) + r"(?![a-z0-9+#])"


def extract_skills(text):
    """Extract and canonicalize known skills from free-form text."""
    lowered = str(text or "").lower()
    found = set()

    for term in SEARCH_TERMS:
        if re.search(_pattern(term), lowered):
            found.add(normalize_skill(term))

    return sorted(found)

