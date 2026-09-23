from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models

from matching.skill_catalog import normalize_skills

# Exactly 10 digits — this is the validator the earlier front-end-only
# check (7-12 digits) is replaced with everywhere in the app.
phone_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="Phone number must be exactly 10 digits.",
)


class CustomUser(AbstractUser):
    """Extends Django's built-in user with a role and a validated phone number."""

    class Role(models.TextChoices):
        RECRUITER = "recruiter", "Recruiter"
        CANDIDATE = "candidate", "Candidate"

    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=10, validators=[phone_validator])

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

    @property
    def is_candidate(self):
        return self.role == self.Role.CANDIDATE


class RecruiterProfile(models.Model):
    """Profile Management -> Recruiter: name, email, company (+ the extra
    fields a real hiring flow needs)."""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="recruiter_profile")

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    company_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=120, blank=True)
    company_website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    company_size = models.CharField(
        max_length=30,
        choices=[
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("201-500", "201-500 employees"),
            ("500+", "500+ employees"),
        ],
        blank=True,
    )
    office_location = models.CharField(max_length=150, blank=True)
    about_company = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} — {self.company_name}"


class CandidateProfile(models.Model):
    """Profile Management -> Candidate: name, email, skills, projects,
    experience (in numbers) — plus every field a resume/profile normally
    needs (education, resume file, links, summary, etc.)."""

    class Qualification(models.TextChoices):
        HIGH_SCHOOL = "high_school", "High School"
        DIPLOMA = "diploma", "Diploma"
        BACHELORS = "bachelors", "Bachelor's Degree"
        MASTERS = "masters", "Master's Degree"
        PHD = "phd", "PhD"

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="candidate_profile")

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=150, blank=True)

    highest_qualification = models.CharField(max_length=20, choices=Qualification.choices, blank=True)
    university = models.CharField(max_length=150, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)

    # "experience in numbers"
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0,
                                            validators=[MinValueValidator(0), MaxValueValidator(50)])
    current_company = models.CharField(max_length=150, blank=True)
    current_designation = models.CharField(max_length=120, blank=True)

    skills = models.TextField(help_text="Comma-separated, e.g. Python, Django, React, SQL")
    # Cached canonical skills used by the skill-gap engine. Keeping a normalized
    # copy avoids re-parsing the candidate profile on every job view.
    parsed_skills = models.JSONField(default=list, blank=True, editable=False)
    projects = models.TextField(blank=True, help_text="Brief description of key projects")

    expected_salary = models.PositiveIntegerField(null=True, blank=True, help_text="Annual, in your local currency")
    notice_period_days = models.PositiveIntegerField(null=True, blank=True)

    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    professional_summary = models.TextField(blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def skills_list(self):
        if self.parsed_skills:
            return sorted(normalize_skills(self.parsed_skills))
        return sorted(normalize_skills(
            [s.strip() for s in self.skills.split(",") if s.strip()]
        ))

    def save(self, *args, **kwargs):
        """Keep canonical candidate skills synchronized with the profile."""
        update_fields = kwargs.get("update_fields")
        if update_fields is None or "skills" in update_fields or "parsed_skills" in update_fields:
            explicit = [s.strip() for s in (self.skills or "").split(",") if s.strip()]
            self.parsed_skills = sorted(normalize_skills(explicit))
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"parsed_skills"}
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
