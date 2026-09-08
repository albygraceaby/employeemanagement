from django.db import models
from jobs.models import Application


class Interview(models.Model):
    MODE_CHOICES = [
        ("online", "Online"),
        ("phone", "Phone"),
        ("onsite", "On-site"),
    ]
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("rescheduled", "Rescheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="interview"
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="online")
    meeting_link_or_venue = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="scheduled")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def candidate(self):
        return self.application.candidate

    @property
    def recruiter(self):
        return self.application.job.recruiter

    @property
    def job(self):
        return self.application.job

    @property
    def scheduled_datetime(self):
        from datetime import datetime
        from django.utils import timezone
        value = datetime.combine(self.scheduled_date, self.scheduled_time)
        return timezone.make_aware(value, timezone.get_current_timezone())

    def sync_application(self):
        app = self.application
        app.status = Application.Status.INTERVIEW
        app.interview_at = self.scheduled_datetime
        app.interview_mode = self.get_mode_display()
        if self.mode == "online":
            app.interview_link = self.meeting_link_or_venue
            app.interview_location = ""
        elif self.mode == "onsite":
            app.interview_location = self.meeting_link_or_venue
            app.interview_link = ""
        else:
            app.interview_link = self.meeting_link_or_venue
            app.interview_location = ""
        app.interview_notes = self.notes
        app.save(update_fields=[
            "status", "interview_at", "interview_mode",
            "interview_link", "interview_location", "interview_notes",
        ])

    def __str__(self):
        return f"{self.candidate.username} - {self.job.title} on {self.scheduled_date}"
