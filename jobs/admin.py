from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "recruiter", "location", "job_type", "openings", "is_active", "posted_at")
    list_filter = ("job_type", "is_active")
    search_fields = ("title", "skills_required", "location")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "applied_at")
    list_filter = ("status",)
