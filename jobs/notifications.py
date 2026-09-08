from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def _send(to_email, subject, body):
    if not to_email:
        return False
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
    return True


def send_application_status_notification(application, old_status):
    """Notify candidate whenever the application status changes."""
    new_status = application.get_status_display()
    candidate_email = getattr(getattr(application.candidate, "candidate_profile", None), "email", None) or application.candidate.email
    subject = f"TalentSphere — Application update for {application.job.title}"
    body = f"""Hello {getattr(getattr(application.candidate, 'candidate_profile', None), 'full_name', application.candidate.username)},

Your application status for "{application.job.title}" has been updated.

Previous status: {dict(application.Status.choices).get(old_status, old_status)}
New status: {new_status}

Company: {getattr(getattr(application.job.recruiter, 'recruiter_profile', None), 'company_name', application.job.recruiter.username)}

Please sign in to TalentSphere Elevate for the latest application details.

Regards,
TalentSphere Elevate
"""
    return _send(candidate_email, subject, body)


def send_interview_scheduled_email(application):
    """Send a dedicated interview email when an interview is scheduled."""
    profile = getattr(application.candidate, "candidate_profile", None)
    candidate_email = getattr(profile, "email", None) or application.candidate.email
    candidate_name = getattr(profile, "full_name", application.candidate.username)
    recruiter_profile = getattr(application.job.recruiter, "recruiter_profile", None)
    company = getattr(recruiter_profile, "company_name", application.job.recruiter.username)

    interview_time = application.interview_at
    if interview_time:
        interview_time = timezone.localtime(interview_time).strftime("%d %b %Y, %I:%M %p")
    else:
        interview_time = "To be confirmed"

    details = [
        f"Interview time: {interview_time}",
        f"Mode: {application.interview_mode or 'To be confirmed'}",
    ]
    if application.interview_link:
        details.append(f"Meeting link: {application.interview_link}")
    if application.interview_location:
        details.append(f"Location: {application.interview_location}")
    if application.interview_notes:
        details.append(f"Notes: {application.interview_notes}")

    subject = f"Interview Scheduled — {application.job.title}"
    body = f"""Hello {candidate_name},

Your interview for "{application.job.title}" at {company} has been scheduled.

{chr(10).join(details)}

Please be ready a few minutes before the scheduled time.

Regards,
TalentSphere Elevate
"""
    return _send(candidate_email, subject, body)
