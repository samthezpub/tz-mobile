from django.urls import path

from users.views import MeView, UsersHealthCheckView


urlpatterns = [
    path("health/", UsersHealthCheckView.as_view(), name="users-health"),
    path("me/", MeView.as_view(), name="users-me"),
]
