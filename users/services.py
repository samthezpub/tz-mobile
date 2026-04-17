from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from users.models import AccessRule


ACTION_PERMISSION_FIELDS = {
    "read": "read_permission",
    "create": "create_permission",
    "update": "update_permission",
    "delete": "delete_permission",
}

ACTION_ALL_PERMISSION_FIELDS = {
    "read": "read_all_permission",
    "update": "update_all_permission",
    "delete": "delete_all_permission",
}


def has_access_permission(user, business_element_code, action, check_all=False):
    permission_field = _get_permission_field(action, check_all)

    if not getattr(user, "is_authenticated", False):
        return False

    role_ids = user.user_roles.values_list("role_id", flat=True)
    if not role_ids:
        return False

    return AccessRule.objects.filter(
        role_id__in=role_ids,
        business_element__code=business_element_code,
        **{permission_field: True},
    ).exists()


def check_access_permission(user, business_element_code, action, check_all=False):
    if not getattr(user, "is_authenticated", False):
        raise NotAuthenticated("Authentication credentials were not provided.")

    if not has_access_permission(user, business_element_code, action, check_all):
        raise PermissionDenied("You do not have permission to perform this action.")

    return True


def _get_permission_field(action, check_all):
    if action not in ACTION_PERMISSION_FIELDS:
        raise ValueError("Unsupported action.")

    if check_all and action in ACTION_ALL_PERMISSION_FIELDS:
        return ACTION_ALL_PERMISSION_FIELDS[action]

    return ACTION_PERMISSION_FIELDS[action]
