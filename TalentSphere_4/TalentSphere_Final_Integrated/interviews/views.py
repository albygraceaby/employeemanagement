from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from jobs.models import Application
from jobs.notifications import send_application_status_notification, send_interview_scheduled_email
from .models import Interview
from .forms import InterviewForm, InterviewStatusForm


@login_required
def schedule_interview(request):
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters can schedule interviews.")
        return redirect("dashboard")

    if request.method == "POST":
        form = InterviewForm(request.POST, recruiter=request.user)
        if form.is_valid():
            interview = form.save()
            interview.sync_application()
            try:
                send_interview_scheduled_email(interview.application)
                messages.success(request, "Interview scheduled and email notification sent.")
            except Exception as exc:
                messages.warning(request, f"Interview scheduled, but email could not be sent: {exc}")
            return redirect("interview_recruiter_dashboard")
    else:
        initial = {}
        application_id = request.GET.get("application_id")
        if application_id:
            app = Application.objects.filter(
                id=application_id, job__recruiter=request.user
            ).first()
            if app and not hasattr(app, "interview"):
                initial["application"] = app
        form = InterviewForm(recruiter=request.user, initial=initial)
    return render(request, "interviews/schedule_interview.html", {"form": form})


@login_required
def recruiter_dashboard(request):
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters can view interview schedules.")
        return redirect("dashboard")
    interviews = Interview.objects.filter(
        application__job__recruiter=request.user
    ).select_related("application__candidate", "application__job")
    return render(request, "interviews/recruiter_dashboard.html", {
        "recruiter": request.user,
        "interviews": interviews,
    })


@login_required
def candidate_dashboard(request):
    if not request.user.is_candidate:
        messages.error(request, "Only candidates can view interviews.")
        return redirect("dashboard")
    interviews = Interview.objects.filter(
        application__candidate=request.user
    ).select_related("application__job", "application__job__recruiter")
    return render(request, "interviews/candidate_dashboard.html", {
        "candidate": request.user,
        "interviews": interviews,
    })


@login_required
def update_interview_status(request, interview_id):
    interview = get_object_or_404(
        Interview, id=interview_id, application__job__recruiter=request.user
    )
    old_status = interview.status
    if request.method == "POST":
        form = InterviewStatusForm(request.POST, instance=interview)
        if form.is_valid():
            updated = form.save()
            updated.sync_application()
            # Preserve the dedicated interview lifecycle status while keeping
            # Application.status as INTERVIEW for scheduled/rescheduled.
            if updated.status in ("completed", "cancelled"):
                app = updated.application
                app.status = Application.Status.SELECTED if updated.status == "completed" else Application.Status.REJECTED
                app.save(update_fields=["status"])
            try:
                send_application_status_notification(
                    updated.application, old_status
                )
                messages.success(request, "Interview updated and status notification sent.")
            except Exception as exc:
                messages.warning(request, f"Interview updated, but email could not be sent: {exc}")
            return redirect("interview_recruiter_dashboard")
    else:
        form = InterviewStatusForm(instance=interview)
    return render(request, "interviews/update_status.html", {
        "form": form, "interview": interview,
    })
