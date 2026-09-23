from django.conf import settings
from django.db import models

from matching.skill_catalog import extract_skills, normalize_skills


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        INTERNSHIP = "internship", "Internship"
        CONTRACT = "contract", "Contract"
        REMOTE = "remote", "Remote"

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posted_jobs",
        limit_choices_to={"role": "recruiter"},
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    skills_required = models.TextField(help_text="Comma-separated, e.g. Python, Django, SQL")
    # Cached canonical skills extracted from the complete job posting. This is
    # populated when the job is saved so candidate requests never re-run text
    # extraction for the same job.
    parsed_skills = models.JSONField(default=list, blank=True, editable=False)
    location = models.CharField(max_length=150)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_required = models.CharField(max_length=60, help_text="e.g. 2-4 years", blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    openings = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["is_active", "-posted_at"], name="jobs_job_active_posted_idx"),
            models.Index(fields=["recruiter", "-posted_at"], name="jobs_job_recruiter_posted_idx"),
        ]

    def save(self, *args, **kwargs):
        """Cache canonical skills whenever the job content changes."""
        update_fields = kwargs.get("update_fields")
        skill_fields = {"title", "description", "responsibilities", "skills_required", "parsed_skills"}
        if update_fields is None or skill_fields.intersection(update_fields):
            text = " ".join([
                self.title or "",
                self.description or "",
                self.responsibilities or "",
                self.skills_required or "",
            ])
            explicit = [s.strip() for s in (self.skills_required or "").split(",") if s.strip()]
            self.parsed_skills = sorted(
                normalize_skills(explicit + extract_skills(text))
            )
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"parsed_skills"}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} @ {self.recruiter.recruiter_profile.company_name if hasattr(self.recruiter, 'recruiter_profile') else self.recruiter.username}"

    def skills_list(self):
        return [s.strip() for s in self.skills_required.split(",") if s.strip()]

    @property
    def applicant_count(self):
        return self.applications.count()


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        SELECTED = "selected", "Selected"
        INTERVIEW = "interview", "Interview"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications",
        limit_choices_to={"role": "candidate"},
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    cover_note = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Recruiter's private notes about this applicant")
    applied_at = models.DateTimeField(auto_now_add=True)
    interview_at = models.DateTimeField(null=True, blank=True)
    interview_mode = models.CharField(max_length=30, blank=True, help_text="Online, Phone, or On-site")
    interview_link = models.URLField(blank=True)
    interview_location = models.CharField(max_length=255, blank=True)
    interview_notes = models.TextField(blank=True)
    last_notified_status = models.CharField(max_length=20, blank=True)

    # Persisted AI/ATS analysis — populated by "Analyze" / "Bulk analyze".
    match_score = models.FloatField(null=True, blank=True, help_text="Overall AI match percentage")
    skill_match_score = models.FloatField(null=True, blank=True, help_text="Skill match percentage")
    experience_match_score = models.FloatField(null=True, blank=True, help_text="Experience match percentage")
    ai_recommendation = models.CharField(max_length=255, blank=True, help_text="AI-generated recommendation label")
    analyzed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("job", "candidate")
        ordering = ["-applied_at"]
        indexes = [
            models.Index(fields=["candidate", "-applied_at"], name="jobs_app_candidate_applied_idx"),
            models.Index(fields=["job", "-applied_at"], name="jobs_app_job_applied_idx"),
            models.Index(fields=["job", "status"], name="jobs_app_job_status_idx"),
            models.Index(fields=["candidate", "status"], name="jobs_app_cand_status_idx"),
            models.Index(fields=["status", "-applied_at"], name="jobs_app_status_applied_idx"),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.candidate.username} -> {self.job.title} ({self.status})"

