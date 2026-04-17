from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import AccessRule
from users.serializers import AccessRuleSerializer
from users.services import check_admin_role


class AccessRuleListView(APIView):
    def get(self, request):
        check_admin_role(request.user)
        access_rules = AccessRule.objects.select_related(
            "role",
            "business_element",
        ).all()
        serializer = AccessRuleSerializer(access_rules, many=True)
        return Response({"items": serializer.data})


class AccessRuleUpdateView(APIView):
    def patch(self, request, pk):
        check_admin_role(request.user)
        access_rule = get_object_or_404(
            AccessRule.objects.select_related(
                "role",
                "business_element",
            ),
            pk=pk,
        )
        serializer = AccessRuleSerializer(
            access_rule,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Access rule updated successfully.",
                "item": serializer.data,
            }
        )
