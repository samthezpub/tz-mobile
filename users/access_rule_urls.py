from django.urls import path

from users.access_rule_views import AccessRuleListView, AccessRuleUpdateView


urlpatterns = [
    path("", AccessRuleListView.as_view(), name="access-rules-list"),
    path("<int:pk>/", AccessRuleUpdateView.as_view(), name="access-rules-update"),
]
