from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_blacklistedtoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="BusinessElement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=100, unique=True)),
                ("name", models.CharField(max_length=150)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="AccessRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("read_permission", models.BooleanField(default=False)),
                ("read_all_permission", models.BooleanField(default=False)),
                ("create_permission", models.BooleanField(default=False)),
                ("update_permission", models.BooleanField(default=False)),
                ("update_all_permission", models.BooleanField(default=False)),
                ("delete_permission", models.BooleanField(default=False)),
                ("delete_all_permission", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "business_element",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="access_rules",
                        to="users.businesselement",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="access_rules",
                        to="users.role",
                    ),
                ),
            ],
            options={
                "ordering": ["role__name", "business_element__name"],
            },
        ),
        migrations.CreateModel(
            name="UserRole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="user_roles",
                        to="users.role",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="user_roles",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "ordering": ["role__name"],
            },
        ),
        migrations.AddConstraint(
            model_name="accessrule",
            constraint=models.UniqueConstraint(
                fields=("role", "business_element"),
                name="unique_role_business_element_rule",
            ),
        ),
        migrations.AddConstraint(
            model_name="userrole",
            constraint=models.UniqueConstraint(
                fields=("user", "role"),
                name="unique_user_role",
            ),
        ),
    ]
