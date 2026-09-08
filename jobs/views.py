from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .forms import JobForm, ApplicationStatusForm, ApplyForm
from .models import Job, Application
from matching.services import calculate_skill_match, cached_skill_gap, build_job_match, get_job_analysis_skills
from accounts.models import CandidateProfile
from .notifications import send_application_status_notification, send_interview_scheduled_email


def recruiter_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_recruiter:
            messages.error(request, "Only recruiters can do that.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper


def candidate_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_candidate:
            messages.error(request, "Only candidates can do that.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper


@login_required
@recruiter_required
def post_job_view(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, f'"{job.title}" has been posted.')
            return redirect("recruiter_jobs")
    else:
        form = JobForm()
    return render(request, "jobs/post_job.html", {"form": form})


@login_required
@recruiter_required
def recruiter_jobs_view(request):
    jobs = Job.objects.filter(recruiter=request.user)
    return render(request, "jobs/recruiter_jobs.html", {"jobs": jobs})


@login_required
@recruiter_required
def job_applicants_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = job.applications.select_related("candidate", "candidate__candidate_profile")
    if request.method == "POST":
        app_id = request.POST.get("application_id")
        application = get_object_or_404(Application, id=app_id, job=job)
        old_status = application.status
        old_interview = (application.interview_at, application.interview_link, application.interview_mode, application.interview_location)
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            updated = form.save(commit=False); updated.save()
            try:
                if old_status != updated.status:
                    send_application_status_notification(updated, old_status)
                    updated.last_notified_status = updated.status; updated.save(update_fields=["last_notified_status"])
                new_interview = (updated.interview_at, updated.interview_link, updated.interview_mode, updated.interview_location)
                if updated.status == Application.Status.INTERVIEW and (old_status != Application.Status.INTERVIEW or old_interview != new_interview):
                    send_interview_scheduled_email(updated)
                messages.success(request, "Applicant status updated and notification email sent.")
            except Exception as exc:
                messages.warning(request, f"Status saved, but email notification could not be sent: {exc}")
            return redirect("job_applicants", job_id=job.id)
    return render(request, "jobs/job_applicants.html", {"job": job, "applications": applications})


@login_required
@candidate_required
def job_list_view(request):
    jobs = Job.objects.filter(is_active=True).select_related("recruiter", "recruiter__recruiter_profile")
    applied_job_ids = set(
        Application.objects.filter(candidate=request.user).values_list("job_id", flat=True)
    )
    return render(request, "jobs/job_list.html", {"jobs": jobs, "applied_job_ids": applied_job_ids})


@login_required
@candidate_required
def apply_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)

    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.info(request, "You've already applied to this job.")
        return redirect("job_list")

    if request.method == "POST":
        form = ApplyForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.save()
            messages.success(request, f'Applied to "{job.title}".')
            return redirect("candidate_skill_gap", job_id=job.id)
    else:
        form = ApplyForm()

    profile = get_object_or_404(CandidateProfile, user=request.user)
    job_skills = get_job_analysis_skills(job)
    skill_gap = cached_skill_gap(
        request.user.id,
        profile.skills_list(),
        job.id,
        job_skills,
    )

    return render(
        request,
        "jobs/apply_job.html",
        {
            "job": job,
            "form": form,
            "profile": profile,
            "skill_gap": skill_gap,
        },
    )


@login_required
@recruiter_required
def kuldeep_email_demo_view(request):
    applications = Application.objects.filter(job__recruiter=request.user).select_related("job", "candidate", "candidate__candidate_profile")
    selected_id = request.POST.get("application_id") or request.GET.get("application_id")
    selected_application = applications.filter(id=selected_id).first() if selected_id else applications.first()
    result = None
    if request.method == "POST" and selected_application:
        notification_type = request.POST.get("notification_type")
        if notification_type == "interview":
            raw=request.POST.get("interview_at") or ""; parsed=parse_datetime(raw) if raw else None
            if parsed and timezone.is_naive(parsed): parsed=timezone.make_aware(parsed, timezone.get_current_timezone())
            selected_application.interview_at=parsed; selected_application.interview_mode=request.POST.get("interview_mode","")
            selected_application.interview_link=request.POST.get("interview_link",""); selected_application.interview_location=request.POST.get("interview_location",""); selected_application.interview_notes=request.POST.get("interview_notes","")
            try: send_interview_scheduled_email(selected_application); result=("success","Interview Scheduled email triggered successfully.")
            except Exception as exc: result=("error",f"Interview email could not be sent: {exc}")
        elif notification_type == "status":
            old_status=request.POST.get("old_status",Application.Status.APPLIED); selected_application.status=request.POST.get("new_status",Application.Status.SHORTLISTED)
            try: send_application_status_notification(selected_application,old_status); result=("success","Application/Interview Status notification triggered successfully.")
            except Exception as exc: result=("error",f"Status email could not be sent: {exc}")
    return render(request,"jobs/kuldeep_email_demo.html",{"applications":applications,"selected_application":selected_application,"result":result,"status_choices":Application.Status.choices})


@login_required
@recruiter_required
def priority_candidates_view(request):
    """ATS priority ranking across the recruiter's applicants."""
    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        "job", "candidate", "candidate__candidate_profile"
    )

    status_filter = request.GET.get("status", "").strip().lower()
    min_score_raw = request.GET.get("min_score", "").strip()
    skill_filter = request.GET.get("skill", "").strip().lower()

    ranked = []
    for application in applications:
        profile = getattr(application.candidate, "candidate_profile", None)
        if not profile:
            continue

        match = calculate_skill_match(
            profile.skills_list(),
            get_job_analysis_skills(application.job),
        )

        # Combine skill match with a small experience signal for ATS ranking.
        required_text = application.job.experience_required or ""
        exp_numbers = [float(x) for x in __import__("re").findall(r"\d+(?:\.\d+)?", required_text)]
        required_exp = exp_numbers[0] if exp_numbers else 0
        candidate_exp = float(profile.experience_years or 0)
        exp_score = 100 if required_exp <= 0 else min(100, (candidate_exp / required_exp) * 100)
        ats_score = round((match["match_percentage"] * 0.8) + (exp_score * 0.2), 2)

        ranked.append({
            "application": application,
            "profile": profile,
            "match": match,
            "ats_score": ats_score,
        })

    if status_filter:
        ranked = [x for x in ranked if x["application"].status == status_filter]

    if skill_filter:
        ranked = [
            x for x in ranked
            if any(skill_filter in s.lower() for s in x["profile"].skills_list())
        ]

    if min_score_raw:
        try:
            minimum = float(min_score_raw)
            ranked = [x for x in ranked if x["ats_score"] >= minimum]
        except ValueError:
            pass

    ranked.sort(key=lambda x: (x["ats_score"], x["match"]["match_percentage"]), reverse=True)

    return render(
        request,
        "jobs/priority_candidates.html",
        {
            "ranked_candidates": ranked,
            "status_filter": status_filter,
            "min_score": min_score_raw,
            "skill_filter": skill_filter,
            "status_choices": Application.Status.choices,
        },
    )


def _persist_analysis(application):
    """Run the explainable match/AI-style analysis for one application and save it."""
    profile = getattr(application.candidate, "candidate_profile", None)
    if not profile:
        return None

    result = build_job_match(profile, application.job)

    application.match_score = result["overall_match"]
    application.skill_match_score = result["skill_match"]
    application.experience_match_score = result["experience_match"]
    application.ai_recommendation = f'{result["recommendation_label"]} — {result["recommendation"]}'
    application.analyzed_at = timezone.now()
    application.save(update_fields=[
        "match_score", "skill_match_score", "experience_match_score",
        "ai_recommendation", "analyzed_at",
    ])
    return result


@login_required
@candidate_required
def candidate_skill_gap_view(request, job_id):
    """Show a candidate the skills they are missing for a job they applied to.

    Job skills are cached when the job is saved; candidate skills come from the
    existing profile, which is automatically populated from the uploaded
    resume by accounts.resume_parser.
    """
    application = get_object_or_404(
        Application.objects.select_related("job", "candidate__candidate_profile"),
        job_id=job_id,
        candidate=request.user,
    )
    profile = get_object_or_404(CandidateProfile, user=request.user)

    job_skills = get_job_analysis_skills(application.job)
    result = cached_skill_gap(
        request.user.id,
        profile.skills_list(),
        application.job.id,
        job_skills,
    )

    return render(
        request,
        "jobs/candidate_skill_gap.html",
        {
            "application": application,
            "job": application.job,
            "profile": profile,
            "result": result,
        },
    )


@login_required
@candidate_required
def candidate_skill_gap_api_view(request, job_id):
    """JSON endpoint for the candidate-facing skill-gap analysis.

    Only the logged-in candidate can inspect their own gap. The job is read
    from its cached canonical skills, and the comparison is cached for
    repeated page loads/API clients.
    """
    job = get_object_or_404(Job, id=job_id, is_active=True)
    profile = get_object_or_404(CandidateProfile, user=request.user)

    job_skills = get_job_analysis_skills(job)
    result = cached_skill_gap(
        request.user.id,
        profile.skills_list(),
        job.id,
        job_skills,
    )

    return JsonResponse({
        "job_id": job.id,
        "job_title": job.title,
        "job_skills": job_skills,
        "candidate_skills": profile.skills_list(),
        **result,
    })


@login_required
@recruiter_required
def analyze_application_view(request, job_id, application_id):
    """Run and persist the AI-style match analysis for a single applicant."""
    application = get_object_or_404(
        Application.objects.select_related("candidate", "candidate__candidate_profile", "job"),
        id=application_id, job_id=job_id, job__recruiter=request.user,
    )
    profile = getattr(application.candidate, "candidate_profile", None)
    if not profile:
        messages.error(request, "This candidate hasn't completed their profile yet.")
        return redirect("job_applicants", job_id=job_id)

    result = _persist_analysis(application)
    return render(
        request,
        "jobs/application_analysis.html",
        {"application": application, "profile": profile, "result": result},
    )


@login_required
@recruiter_required
def bulk_analyze_applications_view(request, job_id):
    """Analyze every applicant for a job in one pass and show them ranked."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = job.applications.select_related("candidate", "candidate__candidate_profile")

    analyzed = 0
    skipped = 0
    results = []
    for application in applications:
        result = _persist_analysis(application)
        if result is None:
            skipped += 1
            continue
        analyzed += 1
        results.append({"application": application, "result": result})

    results.sort(key=lambda item: item["result"]["overall_match"], reverse=True)

    messages.success(
        request,
        f"Analyzed {analyzed} of {applications.count()} application(s)."
        + (f" {skipped} skipped (no profile)." if skipped else ""),
    )
    return render(
        request,
        "jobs/bulk_analysis.html",
        {"job": job, "results": results, "analyzed": analyzed, "total": applications.count()},
    )


@login_required
@recruiter_required
def rank_job_applications_view(request, job_id):
    """AI-ranked applicant list scoped to a single job posting."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = job.applications.select_related("candidate", "candidate__candidate_profile")

    ranked = []
    for application in applications:
        profile = getattr(application.candidate, "candidate_profile", None)
        if not profile:
            continue
        result = build_job_match(profile, job)
        ranked.append({"application": application, "profile": profile, "result": result})

    ranked.sort(key=lambda item: item["result"]["overall_match"], reverse=True)

    return render(
        request,
        "jobs/ranked_applications.html",
        {"job": job, "ranked": ranked},
    )
