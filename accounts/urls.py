from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("frontend-error-demo/", views.frontend_error_demo_view, name="frontend_error_demo"),
    path("dashboard/recruiter-metrics/", views.recruiter_metrics_view, name="recruiter_metrics"),
    path("dashboard/candidate-metrics/", views.candidate_metrics_view, name="candidate_metrics"),
    path("profile/", views.candidate_profile_view, name="candidate_profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path("candidates/", views.candidates_list_view, name="candidates_list"),
    path("candidates/<int:user_id>/", views.view_profile, name="view_candidate_profile"),
]

from .views import analytics_view
urlpatterns += [path("analytics/", analytics_view, name="analytics")]
