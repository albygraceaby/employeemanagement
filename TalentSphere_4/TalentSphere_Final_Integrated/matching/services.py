import hashlib
import re

from django.core.cache import cache
from .skill_catalog import (
    extract_skills,
    get_skill_category,
    get_skill_criticality,
    normalize_skill,
    normalize_skills,
)


def _required_experience_years(experience_required):
    """Read the minimum experience number from values such as '1-2 years'."""
    numbers = re.findall(r"\d+(?:\.\d+)?", str(experience_required or ""))
    return float(numbers[0]) if numbers else 0.0


def _experience_match(candidate_experience, experience_required):
    """Return a 0-100 experience fit score."""
    required = _required_experience_years(experience_required)
    candidate = float(candidate_experience or 0)
    if required <= 0:
        return 100.0
    return round(min(100.0, (candidate / required) * 100.0), 2)


def _keyword_match(candidate_skills, job):
    """
    Estimate keyword relevance by checking candidate skills against the
    complete job text. This is intentionally simple and explainable for a
    student/demo project.
    """
    candidate = {
        normalize_skill(skill)
        for skill in (candidate_skills or [])
        if str(skill).strip()
    }
    job_text = " ".join([
        str(getattr(job, "title", "") or ""),
        str(getattr(job, "description", "") or ""),
        str(getattr(job, "responsibilities", "") or ""),
        str(getattr(job, "skills_required", "") or ""),
    ]).lower()

    if not candidate:
        return 0.0
    matched = [skill for skill in candidate if skill and skill in job_text]
    return round((len(matched) / len(candidate)) * 100.0, 2)


def _recommendation(overall):
    if overall >= 80:
        return "Excellent Match", "Strong fit — highly recommended for application."
    if overall >= 60:
        return "Good Match", "Good fit — consider applying after reviewing the requirements."
    if overall >= 40:
        return "Potentially Suitable", "Potentially suitable — consider the missing skills before applying."
    return "Low Match", "Limited match — upskilling may improve suitability."


def extract_job_skills(job):
    """Extract skills from the full job description, plus the explicit skills field.

    The explicit skills field remains supported, while the description and
    responsibilities are analyzed too. This makes the candidate-facing gap
    analysis truly based on the complete job posting.
    """
    job_text = " ".join([
        str(getattr(job, "title", "") or ""),
        str(getattr(job, "description", "") or ""),
        str(getattr(job, "responsibilities", "") or ""),
        str(getattr(job, "skills_required", "") or ""),
    ])
    return sorted(
        normalize_skills(
            list(getattr(job, "skills_required", "") and job.skills_list() or [])
            + extract_skills(job_text)
        )
    )


def get_job_analysis_skills(job):
    """Return cached job skills, with a safe fallback for older job rows."""
    cached = getattr(job, "parsed_skills", None)
    if cached:
        return sorted(normalize_skills(cached))

    skills = extract_job_skills(job)

    # Backfill a legacy job lazily. This is only a one-time write per legacy job.
    if skills:
        type(job).objects.filter(pk=job.pk, parsed_skills=[]).update(parsed_skills=skills)
    return skills


def calculate_skill_match(candidate_skills, required_skills):
    """
    Compare candidate skills against job-required skills.

    Returns deterministic matching skills, missing skills, category breakdown,
    and urgency level for each missing skill to drive personalized learning paths.
    """
    candidate = normalize_skills(candidate_skills or [])
    required = normalize_skills(required_skills or [])

    matching = sorted(candidate.intersection(required))
    missing = sorted(required.difference(candidate))

    if not required:
        percentage = 0.0
    else:
        percentage = (len(matching) / len(required)) * 100.0

    missing_skills_detailed = []
    critical_missing_count = 0
    secondary_missing_count = 0

    for skill in missing:
        crit = get_skill_criticality(skill)
        cat = get_skill_category(skill)
        if crit == "Critical Core":
            critical_missing_count += 1
        else:
            secondary_missing_count += 1

        missing_skills_detailed.append({
            "name": skill,
            "category": cat,
            "criticality": crit,
            "urgency_score": 90 if crit == "Critical Core" else 50,
        })

    # Group skills by category for granular visual breakdown
    category_breakdown = {}
    for skill in required:
        cat = get_skill_category(skill)
        if cat not in category_breakdown:
            category_breakdown[cat] = {"total": 0, "matched": 0, "percentage": 0.0}
        category_breakdown[cat]["total"] += 1
        if skill in candidate:
            category_breakdown[cat]["matched"] += 1

    for cat, data in category_breakdown.items():
        if data["total"] > 0:
            data["percentage"] = round((data["matched"] / data["total"]) * 100.0, 1)

    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "missing_skills_detailed": missing_skills_detailed,
        "critical_missing_count": critical_missing_count,
        "secondary_missing_count": secondary_missing_count,
        "category_breakdown": category_breakdown,
        "match_percentage": round(percentage, 2),
        "match_score": len(matching),
        "required_skill_count": len(required),
    }


def cached_skill_gap(candidate_id, candidate_skills, job_id, job_skills):
    """Cache the cheap skill comparison using content-aware cache keys.

    The skill fingerprints are part of the key, so edits to a candidate or
    job automatically produce a new result without requiring wildcard cache
    invalidation.
    """
    candidate_key = "|".join(sorted(normalize_skills(candidate_skills or [])))
    job_key = "|".join(sorted(normalize_skills(job_skills or [])))
    fingerprint = hashlib.sha256(
        f"{candidate_id}:{job_id}:{candidate_key}:{job_key}".encode("utf-8")
    ).hexdigest()[:24]
    key = f"talentsphere:skill-gap:{candidate_id}:{job_id}:{fingerprint}"

    return cache.get_or_set(
        key,
        lambda: calculate_skill_match(candidate_skills, job_skills),
        timeout=300,
    )



def build_job_match(candidate_profile, job):
    """Build the full explainable match breakdown shown on the matches page."""
    skill_match = calculate_skill_match(
        candidate_profile.skills_list(),
        get_job_analysis_skills(job),
    )
    skill_score = skill_match["match_percentage"]
    experience_score = _experience_match(
        candidate_profile.experience_years,
        job.experience_required,
    )
    keyword_score = _keyword_match(candidate_profile.skills_list(), job)

    # Skill fit carries the most weight; experience and keyword relevance
    # provide supporting signals without hiding the underlying skill score.
    overall = round(
        (skill_score * 0.55)
        + (experience_score * 0.25)
        + (keyword_score * 0.20),
        2,
    )
    label, recommendation = _recommendation(overall)

    skill_match.update({
        "skill_match": skill_score,
        "experience_match": experience_score,
        "keyword_match": keyword_score,
        "overall_match": overall,
        "recommendation_label": label,
        "recommendation": recommendation,
    })
    return skill_match


def rank_jobs(candidate_profile, jobs):
    """Return all active jobs ranked from highest to lowest overall match."""
    ranked = []
    for job in jobs:
        result = build_job_match(candidate_profile, job)
        ranked.append({"job": job, "match": result})

    ranked.sort(
        key=lambda item: (
            item["match"]["overall_match"],
            item["match"]["skill_match"],
            item["match"]["match_score"],
        ),
        reverse=True,
    )
    return ranked
