from django.urls import path

from users.views import UsersHealthCheckView


urlpatterns = [
    path("health/", UsersHealthCheckView.as_view(), name="users-health"),
]
