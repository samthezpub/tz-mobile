from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/auth/", include("users.auth_urls")),
    path("api/access-rules/", include("users.access_rule_urls")),
    path("api/", include("users.business_urls")),
]
