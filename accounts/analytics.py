import json

from django.db.models import Count

from jobs.models import Job, Application


def get_dashboard_analytics(user):
    """Return the recruiter + candidate analytics shown on the Analytics page."""
    # Platform-level metrics (useful for the combined analytics dashboard).
    total_jobs_posted = Job.objects.count()
    total_applications = Application.objects.count()
    total_interviews = Application.objects.filter(status=Application.Status.INTERVIEW).count()
    total_selected = Application.objects.filter(status=Application.Status.SELECTED).count()
    total_rejected = Application.objects.filter(status=Application.Status.REJECTED).count()
    total_shortlisted = Application.objects.filter(status=Application.Status.SHORTLISTED).count()
    total_candidates = Application.objects.values("candidate_id").distinct().count()
    total_recruiters = Job.objects.values("recruiter_id").distinct().count()

    # Current-user metrics.
    if user.is_candidate:
        applications = Application.objects.filter(candidate=user)
        current = {
            "jobs_posted": 0,
            "applications_received": 0,
            "candidates_interviewed": 0,
            "jobs_applied": applications.count(),
            "applied": applications.filter(status=Application.Status.APPLIED).count(),
            "shortlisted": applications.filter(status=Application.Status.SHORTLISTED).count(),
            "interviewed": applications.filter(status=Application.Status.INTERVIEW).count(),
            "selected": applications.filter(status=Application.Status.SELECTED).count(),
            "rejected": applications.filter(status=Application.Status.REJECTED).count(),
        }
    else:
        jobs = Job.objects.filter(recruiter=user)
        applications = Application.objects.filter(job__recruiter=user)
        current = {
            "jobs_posted": jobs.count(),
            "applications_received": applications.count(),
            "candidates_interviewed": applications.filter(status=Application.Status.INTERVIEW).count(),
            "jobs_applied": 0,
            "applied": 0,
            "shortlisted": applications.filter(status=Application.Status.SHORTLISTED).count(),
            "interviewed": applications.filter(status=Application.Status.INTERVIEW).count(),
            "selected": applications.filter(status=Application.Status.SELECTED).count(),
            "rejected": applications.filter(status=Application.Status.REJECTED).count(),
        }

    # Application-status chart for the complete dashboard.
    status_data = [
        total_applications,
        total_shortlisted,
        total_interviews,
        total_selected,
        total_rejected,
    ]

    # Recruiter vs candidate summary chart.
    role_data = [total_recruiters, total_candidates]

    return {
        "total_jobs_posted": total_jobs_posted,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
        "total_selected": total_selected,
        "total_rejected": total_rejected,
        "total_shortlisted": total_shortlisted,
        "total_candidates": total_candidates,
        "total_recruiters": total_recruiters,
        "current": current,
        "status_chart_data": json.dumps(status_data),
        "role_chart_data": json.dumps(role_data),
        # Backward-compatible keys for any older template/code.
        "total_views": total_candidates,
        "active_applications": total_applications - total_rejected,
        "profile_matches": total_shortlisted,
        "chart_data": json.dumps(status_data),
    }
