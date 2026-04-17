from django.db import migrations


def create_rbac_seed_data(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    BusinessElement = apps.get_model("users", "BusinessElement")
    AccessRule = apps.get_model("users", "AccessRule")

    roles = {
        "admin": Role.objects.get_or_create(
            name="admin",
            defaults={"description": "Full access to all business elements."},
        )[0],
        "manager": Role.objects.get_or_create(
            name="manager",
            defaults={"description": "Manage users and view access settings."},
        )[0],
        "user": Role.objects.get_or_create(
            name="user",
            defaults={"description": "Basic access to own profile only."},
        )[0],
    }

    business_elements = {
        "profile": BusinessElement.objects.get_or_create(
            code="profile",
            defaults={"name": "Profile", "description": "Current user profile."},
        )[0],
        "users": BusinessElement.objects.get_or_create(
            code="users",
            defaults={"name": "Users", "description": "Users management."},
        )[0],
        "roles": BusinessElement.objects.get_or_create(
            code="roles",
            defaults={"name": "Roles", "description": "Roles management."},
        )[0],
        "access_rules": BusinessElement.objects.get_or_create(
            code="access_rules",
            defaults={
                "name": "Access Rules",
                "description": "Access rules management.",
            },
        )[0],
    }

    for business_element in business_elements.values():
        AccessRule.objects.get_or_create(
            role=roles["admin"],
            business_element=business_element,
            defaults={
                "read_permission": True,
                "read_all_permission": True,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": True,
                "delete_permission": True,
                "delete_all_permission": True,
            },
        )

    AccessRule.objects.get_or_create(
        role=roles["manager"],
        business_element=business_elements["users"],
        defaults={
            "read_permission": True,
            "read_all_permission": True,
            "create_permission": True,
            "update_permission": True,
            "update_all_permission": True,
        },
    )
    AccessRule.objects.get_or_create(
        role=roles["manager"],
        business_element=business_elements["roles"],
        defaults={
            "read_permission": True,
            "read_all_permission": True,
        },
    )
    AccessRule.objects.get_or_create(
        role=roles["manager"],
        business_element=business_elements["profile"],
        defaults={
            "read_permission": True,
            "update_permission": True,
        },
    )

    AccessRule.objects.get_or_create(
        role=roles["user"],
        business_element=business_elements["profile"],
        defaults={
            "read_permission": True,
            "update_permission": True,
        },
    )


def remove_rbac_seed_data(apps, schema_editor):
    AccessRule = apps.get_model("users", "AccessRule")
    BusinessElement = apps.get_model("users", "BusinessElement")
    Role = apps.get_model("users", "Role")

    AccessRule.objects.filter(
        role__name__in=["admin", "manager", "user"]
    ).delete()
    BusinessElement.objects.filter(
        code__in=["profile", "users", "roles", "access_rules"]
    ).delete()
    Role.objects.filter(name__in=["admin", "manager", "user"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_rbac_models"),
    ]

    operations = [
        migrations.RunPython(create_rbac_seed_data, remove_rbac_seed_data),
    ]
