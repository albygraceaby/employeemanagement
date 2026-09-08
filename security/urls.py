from django.urls import path
from .views import token_view, refresh_view, me_view

urlpatterns = [
    path("token/", token_view, name="jwt_token"),
    path("refresh/", refresh_view, name="jwt_refresh"),
    path("me/", me_view, name="jwt_me"),
]
