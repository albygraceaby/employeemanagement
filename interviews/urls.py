from django.urls import path
from . import views

urlpatterns = [
    path("schedule/", views.schedule_interview, name="schedule_interview"),
    path("recruiter/", views.recruiter_dashboard, name="interview_recruiter_dashboard"),
    path("candidate/", views.candidate_dashboard, name="interview_candidate_dashboard"),
    path("<int:interview_id>/status/", views.update_interview_status, name="update_interview_status"),
]
