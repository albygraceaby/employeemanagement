from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="matching-home"),
    path("apply/<int:job_id>/", views.apply_match_view, name="matching-apply"),
    path("candidates/", views.candidate_recommendations_view, name="matching-candidates"),
    path("learning-path/<int:job_id>/", views.candidate_learning_path_view, name="candidate_learning_path"),
    path("learning-path/skill/<str:skill_name>/", views.skill_learning_roadmap_view, name="skill_learning_roadmap"),
    path("learning-path/api/<int:job_id>/", views.candidate_learning_path_api_view, name="candidate_learning_path_api"),
]

