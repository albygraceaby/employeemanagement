from django.urls import path
from . import views

urlpatterns = [
    path("post/", views.post_job_view, name="post_job"),
    path("mine/", views.recruiter_jobs_view, name="recruiter_jobs"),
    path("priority-candidates/", views.priority_candidates_view, name="priority_candidates"),
    path("kuldeep-email-demo/", views.kuldeep_email_demo_view, name="kuldeep_email_demo"),
    path("<int:job_id>/applicants/", views.job_applicants_view, name="job_applicants"),
    path("browse/", views.job_list_view, name="job_list"),
    path("<int:job_id>/apply/", views.apply_job_view, name="apply_job"),
    path("<int:job_id>/skill-gap/", views.candidate_skill_gap_view, name="candidate_skill_gap"),
    path("<int:job_id>/skill-gap/api/", views.candidate_skill_gap_api_view, name="candidate_skill_gap_api"),
    path("<int:job_id>/applicants/<int:application_id>/analyze/", views.analyze_application_view, name="analyze_application"),
    path("<int:job_id>/bulk-analyze/", views.bulk_analyze_applications_view, name="bulk_analyze_applications"),
    path("<int:job_id>/rank/", views.rank_job_applications_view, name="rank_job_applications"),
]
