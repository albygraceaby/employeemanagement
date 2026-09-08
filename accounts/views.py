from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from jobs.models import Job, Application
from .forms import SignupForm, LoginForm, RecruiterProfileForm, CandidateProfileForm
from .models import CustomUser, RecruiterProfile, CandidateProfile
from .resume_parser import apply_extracted_profile_data
from matching.services import rank_jobs


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    initial_role = request.GET.get("role", CustomUser.Role.CANDIDATE)

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    password=data["password"],
                    phone=data["phone"],
                    role=data["role"],
                )
                if data["role"] == CustomUser.Role.RECRUITER:
                    RecruiterProfile.objects.create(
                        user=user, full_name=data["username"], email=data["email"], company_name="",
                    )
                else:
                    CandidateProfile.objects.create(
                        user=user, full_name=data["username"], email=data["email"], skills="",
                    )
            auth_login(request, user)
            messages.success(request, "Account created. Let's finish setting up your profile.")
            return redirect("edit_profile")
        return render(request, "accounts/signup.html", {"form": form, "role": data_role_fallback(form)})

    form = SignupForm(initial={"role": initial_role})
    return render(request, "accounts/signup.html", {"form": form, "role": initial_role})


def data_role_fallback(form):
    return form.data.get("role", CustomUser.Role.CANDIDATE)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("dashboard")
        messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm(request)
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    user = request.user
    if user.is_recruiter:
        jobs = Job.objects.filter(recruiter=user).order_by("-posted_at")
        current_job = jobs.first()
        recruiter_applications = Application.objects.filter(job__recruiter=user)
        total_applicants = recruiter_applications.count()
        candidates_interviewed = (
            recruiter_applications
            .filter(status__in=[Application.Status.INTERVIEW, Application.Status.SELECTED])
            .values("candidate_id")
            .distinct()
            .count()
        )
        context = {
            "jobs": jobs,
            "jobs_posted_count": jobs.count(),
            "current_job": current_job,
            "total_applicants": total_applicants,
            "candidates_interviewed": candidates_interviewed,
        }
        return render(request, "dashboard/recruiter_dashboard.html", context)
    else:
        applications = Application.objects.filter(candidate=user).select_related("job")
        total_jobs_applied = applications.count()
        applied_count = applications.filter(status=Application.Status.APPLIED).count()
        shortlisted_count = applications.filter(status=Application.Status.SHORTLISTED).count()
        interviewed_count = applications.filter(status=Application.Status.INTERVIEW).count()
        selected_count = applications.filter(status=Application.Status.SELECTED).count()
        rejected_count = applications.filter(status=Application.Status.REJECTED).count()
        open_jobs_count = Job.objects.filter(is_active=True).count()
        context = {
            "applications": applications,
            "total_jobs_applied": total_jobs_applied,
            "applied_count": applied_count,
            "shortlisted_count": shortlisted_count,
            "interviewed_count": interviewed_count,
            "selected_count": selected_count,
            "rejected_count": rejected_count,
            "open_jobs_count": open_jobs_count,
        }
        return render(request, "dashboard/candidate_dashboard.html", context)



@login_required
def candidate_profile_view(request):
    """Candidate's own profile page with skills, experience, projects and job matches."""
    if not request.user.is_candidate:
        messages.error(request, "Only candidates can view this profile page.")
        return redirect("dashboard")

    profile = get_object_or_404(CandidateProfile, user=request.user)
    jobs = Job.objects.filter(is_active=True).select_related(
        "recruiter", "recruiter__recruiter_profile"
    )
    ranked_jobs = rank_jobs(profile, jobs)
    applied_job_ids = set(
        Application.objects.filter(candidate=request.user).values_list("job_id", flat=True)
    )

    return render(
        request,
        "accounts/candidate_profile_view.html",
        {
            "profile": profile,
            "ranked_jobs": ranked_jobs[:6],
            "applied_job_ids": applied_job_ids,
        },
    )

@login_required
def edit_profile_view(request):
    user = request.user
    if user.is_recruiter:
        profile, _ = RecruiterProfile.objects.get_or_create(
            user=user, defaults={"full_name": user.username, "email": user.email, "company_name": ""}
        )
        form_class = RecruiterProfileForm
        template = "accounts/recruiter_profile.html"
    else:
        profile, _ = CandidateProfile.objects.get_or_create(
            user=user, defaults={"full_name": user.username, "email": user.email, "skills": ""}
        )
        form_class = CandidateProfileForm
        template = "accounts/candidate_profile.html"

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved_profile = form.save()
            if (
                not user.is_recruiter
                and saved_profile.resume
                and "resume" in form.changed_data
            ):
                try:
                    extracted = apply_extracted_profile_data(
                        saved_profile, saved_profile.resume.path
                    )
                    if extracted["text"]:
                        messages.success(
                            request,
                            "Profile updated and resume information was extracted successfully."
                        )
                    else:
                        messages.success(
                            request,
                            "Profile updated. Resume uploaded; text extraction was unavailable for this file."
                        )
                except Exception:
                    messages.success(
                        request,
                        "Profile updated. Resume uploaded; automatic extraction could not be completed."
                    )
            else:
                messages.success(request, "Profile updated successfully.")
            return redirect("dashboard")
    else:
        form = form_class(instance=profile)

    return render(request, template, {"form": form, "profile": profile})


@login_required
def view_profile(request, user_id):
    """Recruiter viewing a specific candidate's full profile (scoped to candidates who applied to recruiter's jobs)."""
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters can view candidate profiles.")
        return redirect("dashboard")
    candidate_user = get_object_or_404(CustomUser, id=user_id, role=CustomUser.Role.CANDIDATE)
    has_applied = Application.objects.filter(candidate=candidate_user, job__recruiter=request.user).exists()
    if not has_applied:
        messages.error(request, "You can only view profiles of candidates who have applied to your company.")
        return redirect("candidates_list")
    profile = get_object_or_404(CandidateProfile, user=candidate_user)
    return render(request, "accounts/candidate_profile_readonly.html", {"profile": profile})


@user_passes_test(lambda u: u.is_active and u.is_recruiter)
def recruiter_metrics_view(request):
    """Recruiter Metrics for the currently logged-in recruiter only.

    The project requirement is recruiter-specific: show how many jobs the
    recruiter posted, how many applications those jobs received, and how many
    candidates they interviewed. Do not mix in other recruiters' data.
    """
    interviewed_statuses = [Application.Status.INTERVIEW, Application.Status.SELECTED]

    recruiter_jobs = Job.objects.filter(recruiter=request.user)
    recruiter_applications = Application.objects.filter(job__recruiter=request.user)

    total_jobs_posted = recruiter_jobs.count()
    total_applications_received = recruiter_applications.count()
    total_candidates_interviewed = (
        recruiter_applications
        .filter(status__in=interviewed_statuses)
        .values("candidate_id")
        .distinct()
        .count()
    )

    # Keep the existing table structure, but scope it to the logged-in
    # recruiter so another recruiter's metrics cannot appear here.
    recruiter = (
        CustomUser.objects.filter(pk=request.user.pk)
        .select_related("recruiter_profile")
        .annotate(
            jobs_posted=Count("posted_jobs", distinct=True),
            applications_received=Count("posted_jobs__applications", distinct=True),
            candidates_interviewed=Count(
                "posted_jobs__applications__candidate",
                filter=Q(posted_jobs__applications__status__in=interviewed_statuses),
                distinct=True,
            ),
        )
    )

    context = {
        "total_jobs_posted": total_jobs_posted,
        "total_applications_received": total_applications_received,
        "total_candidates_interviewed": total_candidates_interviewed,
        "recruiters": recruiter,
    }
    return render(request, "dashboard/recruiter_metrics.html", context)


@login_required
def candidate_metrics_view(request):
    """Candidate Metrics:
    Total Jobs Applied, status counts (Applied, Shortlisted, Interviewed, Selected, Rejected),
    and Candidate-wise Statistics.
    Recruiters see metrics for candidates who applied to their company;
    candidates see only their own metrics.
    """
    user = request.user
    if user.is_recruiter:
        app_qs = Application.objects.filter(job__recruiter=user)
        candidates_qs = CustomUser.objects.filter(
            role=CustomUser.Role.CANDIDATE,
            applications__job__recruiter=user
        ).distinct()

        candidates = (
            candidates_qs
            .select_related("candidate_profile")
            .annotate(
                total_applied=Count(
                    "applications",
                    filter=Q(applications__job__recruiter=user),
                    distinct=True
                ),
                status_applied=Count(
                    "applications",
                    filter=Q(applications__job__recruiter=user, applications__status=Application.Status.APPLIED),
                    distinct=True
                ),
                status_shortlisted=Count(
                    "applications",
                    filter=Q(applications__job__recruiter=user, applications__status=Application.Status.SHORTLISTED),
                    distinct=True
                ),
                status_interviewed=Count(
                    "applications",
                    filter=Q(applications__job__recruiter=user, applications__status=Application.Status.INTERVIEW),
                    distinct=True
                ),
                status_selected=Count(
                    "applications",
                    filter=Q(applications__job__recruiter=user, applications__status=Application.Status.SELECTED),
                    distinct=True
                ),
                status_rejected=Count(
                    "applications",
                    filter=Q(applications__job__recruiter=user, applications__status=Application.Status.REJECTED),
                    distinct=True
                ),
            )
            .order_by("-total_applied", "username")
        )
    else:
        app_qs = Application.objects.filter(candidate=user)
        candidates_qs = CustomUser.objects.filter(pk=user.pk)

        candidates = (
            candidates_qs
            .select_related("candidate_profile")
            .annotate(
                total_applied=Count("applications", distinct=True),
                status_applied=Count(
                    "applications",
                    filter=Q(applications__status=Application.Status.APPLIED),
                    distinct=True,
                ),
                status_shortlisted=Count(
                    "applications",
                    filter=Q(applications__status=Application.Status.SHORTLISTED),
                    distinct=True,
                ),
                status_interviewed=Count(
                    "applications",
                    filter=Q(applications__status=Application.Status.INTERVIEW),
                    distinct=True,
                ),
                status_selected=Count(
                    "applications",
                    filter=Q(applications__status=Application.Status.SELECTED),
                    distinct=True,
                ),
                status_rejected=Count(
                    "applications",
                    filter=Q(applications__status=Application.Status.REJECTED),
                    distinct=True,
                ),
            )
            .order_by("-total_applied", "username")
        )

    total_jobs_applied = app_qs.count()
    applied_count = app_qs.filter(status=Application.Status.APPLIED).count()
    shortlisted_count = app_qs.filter(status=Application.Status.SHORTLISTED).count()
    interviewed_count = app_qs.filter(status=Application.Status.INTERVIEW).count()
    selected_count = app_qs.filter(status=Application.Status.SELECTED).count()
    rejected_count = app_qs.filter(status=Application.Status.REJECTED).count()

    detailed_applications = (
        app_qs
        .select_related("job", "job__recruiter", "job__recruiter__recruiter_profile", "candidate", "candidate__candidate_profile")
        .order_by("-applied_at")
    )

    context = {
        "total_jobs_applied": total_jobs_applied,
        "applied_count": applied_count,
        "shortlisted_count": shortlisted_count,
        "interviewed_count": interviewed_count,
        "selected_count": selected_count,
        "rejected_count": rejected_count,
        "candidates": candidates,
        "detailed_applications": detailed_applications,
    }
    return render(request, "dashboard/candidate_metrics.html", context)


@login_required
def candidates_list_view(request):
    """Recruiter -> browse candidates who have applied to jobs posted by this recruiter's company."""
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters can view the candidates list.")
        return redirect("dashboard")
    candidates = (
        CandidateProfile.objects
        .filter(user__applications__job__recruiter=request.user)
        .select_related("user")
        .distinct()
        .order_by("-updated_at")
    )
    return render(request, "accounts/candidates_list.html", {"candidates": candidates})


def analytics_view(request):
    from .analytics import get_dashboard_analytics
    analytics = get_dashboard_analytics(request.user)
    return render(request, "analytics/analytics.html", {"analytics": analytics})


@login_required
def frontend_error_demo_view(request):
    return render(request, "accounts/frontend_error_demo.html", {"statuses": [400, 401, 403, 404, 409, 429, 500]})

@login_required
def frontend_error_api(request, status):
    allowed = {400, 401, 403, 404, 409, 429, 500}
    if status not in allowed:
        return JsonResponse({"message": "Unsupported demo status."}, status=400)
    return JsonResponse({"message": f"Demo backend response for HTTP {status}."}, status=status)
