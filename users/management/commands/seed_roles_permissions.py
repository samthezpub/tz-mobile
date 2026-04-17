from django.core.management.base import BaseCommand

from users.models import AccessRule, BusinessElement, Role


ROLE_DEFAULTS = {
    "admin": "Full access to all business elements.",
    "manager": "Can manage catalog and orders data.",
    "user": "Can work only with own orders and available catalog data.",
    "guest": "Can only view limited catalog data.",
}

BUSINESS_ELEMENT_DEFAULTS = {
    "users": {
        "name": "Users",
        "description": "Users management.",
    },
    "products": {
        "name": "Products",
        "description": "Products catalog.",
    },
    "stores": {
        "name": "Stores",
        "description": "Stores directory.",
    },
    "orders": {
        "name": "Orders",
        "description": "Orders processing.",
    },
    "access_rules": {
        "name": "Access Rules",
        "description": "Roles and permissions management.",
    },
}

ACCESS_RULE_DEFAULTS = {
    "admin": {
        "users": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
            "delete_permission": True,
            "delete_all_permission": True,
        },
        "products": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
            "delete_permission": True,
            "delete_all_permission": True,
        },
        "stores": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
            "delete_permission": True,
            "delete_all_permission": True,
        },
        "orders": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
            "delete_permission": True,
            "delete_all_permission": True,
        },
        "access_rules": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
            "delete_permission": True,
            "delete_all_permission": True,
        },
    },
    "manager": {
        "users": {
            "read_permission": True,
            "read_all_permission": True,
            "update_permission": True,
            "update_all_permission": True,
        },
        "products": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
        },
        "stores": {
            "read_permission": True,
            "read_all_permission": True,
            "update_permission": True,
            "update_all_permission": True,
        },
        "orders": {
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
        },
        "access_rules": {
            "read_permission": True,
            "read_all_permission": True,
        },
    },
    "user": {
        "products": {
            "read_permission": True,
        },
        "stores": {
            "read_permission": True,
        },
        "orders": {
            "read_permission": True,
            "create_permission": True,
            "update_permission": True,
        },
    },
    "guest": {
        "products": {
            "read_permission": True,
        },
        "stores": {
            "read_permission": True,
        },
    },
}


class Command(BaseCommand):
    help = "Create test roles, business elements and access rules for RBAC demo."

    def handle(self, *args, **options):
        roles = self._create_roles()
        business_elements = self._create_business_elements()
        self._create_access_rules(roles, business_elements)

        self.stdout.write(
            self.style.SUCCESS("Seed data for roles and permissions created.")
        )

    def _create_roles(self):
        roles = {}
        for role_name, description in ROLE_DEFAULTS.items():
            role, _ = Role.objects.update_or_create(
                name=role_name,
                defaults={"description": description},
            )
            roles[role_name] = role
        return roles

    def _create_business_elements(self):
        business_elements = {}
        for code, defaults in BUSINESS_ELEMENT_DEFAULTS.items():
            business_element, _ = BusinessElement.objects.update_or_create(
                code=code,
                defaults=defaults,
            )
            business_elements[code] = business_element
        return business_elements

    def _create_access_rules(self, roles, business_elements):
        for role_name, rules in ACCESS_RULE_DEFAULTS.items():
            for business_element_code, rule_defaults in rules.items():
                AccessRule.objects.update_or_create(
                    role=roles[role_name],
                    business_element=business_elements[business_element_code],
                    defaults=rule_defaults,
                )
