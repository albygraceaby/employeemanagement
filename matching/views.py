from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CandidateProfile
from jobs.models import Application, Job

from .learning_paths import generate_learning_path, get_skill_learning_roadmap
from .services import build_job_match, cached_skill_gap, get_job_analysis_skills, rank_jobs


def candidate_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_candidate:
            messages.error(request, "Only candidates can use job matching.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper


def recruiter_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_recruiter:
            messages.error(request, "Only recruiters can use candidate recommendations.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper


@login_required
@candidate_required
def home(request):
    """Show active jobs with explainable match breakdowns, paginated for 1000+ jobs."""
    profile = get_object_or_404(CandidateProfile, user=request.user)
    jobs = Job.objects.filter(is_active=True).select_related(
        "recruiter", "recruiter__recruiter_profile"
    )
    ranked_jobs = rank_jobs(profile, jobs)

    applied_job_ids = set(
        Application.objects.filter(candidate=request.user).values_list("job_id", flat=True)
    )

    paginator = Paginator(ranked_jobs, 15)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "matching/home.html",
        {
            "candidate": profile,
            "ranked_jobs": page_obj,
            "page_obj": page_obj,
            "applied_job_ids": applied_job_ids,
        },
    )


@login_required
@candidate_required
def apply_match_view(request, job_id):
    """Apply to a matched job using the existing Application model."""
    if request.method != "POST":
        return redirect("matching-home")

    job = get_object_or_404(Job, id=job_id, is_active=True)
    _, created = Application.objects.get_or_create(
        job=job,
        candidate=request.user,
    )

    if created:
        messages.success(request, f'Applied to "{job.title}".')
    else:
        messages.info(request, "You've already applied to this job.")

    return redirect("candidate_skill_gap", job_id=job.id)


@login_required
@recruiter_required
def candidate_recommendations_view(request):
    """Rank applicants for the recruiter's jobs using the explainable matching engine (paginated)."""
    jobs = Job.objects.filter(recruiter=request.user).order_by("-posted_at")
    applications = Application.objects.filter(job__in=jobs).select_related(
        "candidate", "candidate__candidate_profile", "job"
    )
    job_filter = request.GET.get("job", "").strip()
    if job_filter:
        applications = applications.filter(job_id=job_filter)
    recommended = []
    for application in applications:
        profile = getattr(application.candidate, "candidate_profile", None)
        if not profile:
            continue
        result = build_job_match(profile, application.job)
        recommended.append({"application": application, "profile": profile, "job": application.job, "match": result})
    recommended.sort(key=lambda item: item["match"]["overall_match"], reverse=True)

    paginator = Paginator(recommended, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "matching/candidate_recommendations.html",
        {
            "recommended": page_obj,
            "page_obj": page_obj,
            "jobs": jobs,
            "job_filter": job_filter,
        },
    )


@login_required
@candidate_required
def candidate_learning_path_view(request, job_id):
    """Generate and display personalized learning path suggestions for a job's missing skills."""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    profile = get_object_or_404(CandidateProfile, user=request.user)

    job_skills = get_job_analysis_skills(job)
    gap_result = cached_skill_gap(request.user.id, profile.skills_list(), job.id, job_skills)

    learning_path = generate_learning_path(gap_result["missing_skills"], target_job_title=job.title)

    return render(
        request,
        "matching/learning_path.html",
        {
            "job": job,
            "profile": profile,
            "gap_result": gap_result,
            "learning_path": learning_path,
        },
    )


@login_required
def skill_learning_roadmap_view(request, skill_name):
    """Display a standalone learning path roadmap for any specific technical skill."""
    roadmap = get_skill_learning_roadmap(skill_name)
    return render(
        request,
        "matching/single_skill_roadmap.html",
        {
            "skill_name": skill_name,
            "roadmap": roadmap,
        },
    )


@login_required
@candidate_required
def candidate_learning_path_api_view(request, job_id):
    """JSON REST endpoint for the candidate's learning path for a target job."""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    profile = get_object_or_404(CandidateProfile, user=request.user)

    job_skills = get_job_analysis_skills(job)
    gap_result = cached_skill_gap(request.user.id, profile.skills_list(), job.id, job_skills)
    learning_path = generate_learning_path(gap_result["missing_skills"], target_job_title=job.title)

    return JsonResponse({
        "job_id": job.id,
        "job_title": job.title,
        "candidate_id": request.user.id,
        "gap_analysis": gap_result,
        "learning_path": learning_path,
    })

