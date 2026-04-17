from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import (
    AccessRule,
    BlacklistedToken,
    BusinessElement,
    Role,
    User,
    UserRole,
)
from users.services import check_access_permission, has_access_permission
from users.tokens import create_access_token


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_register_user_successfully(self):
        payload = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "middle_name": "Ivanovich",
            "email": "ivan@example.com",
            "password": "strongpass123",
            "password_repeat": "strongpass123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully.")
        self.assertEqual(response.data["user"]["email"], payload["email"])
        self.assertNotIn("password", response.data["user"])
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())
        self.assertTrue(
            User.objects.get(email=payload["email"]).check_password(payload["password"])
        )

    def test_register_user_with_different_passwords(self):
        payload = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "middle_name": "Ivanovich",
            "email": "ivan@example.com",
            "password": "strongpass123",
            "password_repeat": "otherpass123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_repeat", response.data)

    def test_register_user_with_existing_email(self):
        User.objects.create_user(
            email="ivan@example.com",
            password="strongpass123",
            first_name="Ivan",
            last_name="Ivanov",
            middle_name="Ivanovich",
        )
        payload = {
            "first_name": "Petr",
            "last_name": "Petrov",
            "middle_name": "Petrovich",
            "email": "ivan@example.com",
            "password": "strongpass123",
            "password_repeat": "strongpass123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.me_url = reverse("me")
        self.profile_me_url = reverse("users-me")
        self.user = User.objects.create_user(
            email="ivan@example.com",
            password="strongpass123",
            first_name="Ivan",
            last_name="Ivanov",
            middle_name="Ivanovich",
        )

    def test_login_user_successfully(self):
        payload = {
            "email": "ivan@example.com",
            "password": "strongpass123",
        }

        response = self.client.post(self.login_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_login_user_with_invalid_password(self):
        payload = {
            "email": "ivan@example.com",
            "password": "wrongpass123",
        }

        response = self.client.post(self.login_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    def test_get_me_with_bearer_token(self):
        login_response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_get_me_with_invalid_bearer_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_current_token(self):
        login_response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        logout_response = self.client.post(self.logout_url, format="json")
        me_response = self.client.get(self.me_url)

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertEqual(logout_response.data["message"], "Logout successful.")
        self.assertTrue(BlacklistedToken.objects.filter(token=token).exists())
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_token(self):
        response = self.client.post(self.logout_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_me_with_bearer_token(self):
        login_response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.profile_me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_patch_profile_me_successfully(self):
        login_response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )
        token = login_response.data["token"]

        payload = {
            "first_name": "Petr",
            "middle_name": "Petrovich",
            "email": "petr@example.com",
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.patch(self.profile_me_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Profile updated successfully.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.middle_name, payload["middle_name"])
        self.assertEqual(self.user.email, payload["email"])

    def test_patch_profile_me_with_existing_email(self):
        User.objects.create_user(
            email="other@example.com",
            password="strongpass123",
            first_name="Other",
            last_name="User",
            middle_name="Test",
        )
        login_response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.patch(
            self.profile_me_url,
            {"email": "other@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_patch_profile_me_without_token(self):
        response = self.client.patch(
            self.profile_me_url,
            {"first_name": "Petr"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_profile_me_soft_deletes_user(self):
        login_response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        delete_response = self.client.delete(self.profile_me_url)
        me_response = self.client.get(self.profile_me_url)

        self.assertEqual(delete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.data["message"], "Account deleted successfully.")
        self.assertTrue(BlacklistedToken.objects.filter(token=token).exists())
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_deleted_user_is_forbidden(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.login_url,
            {"email": "ivan@example.com", "password": "strongpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "User account is inactive.")

    def test_delete_profile_me_without_token(self):
        response = self.client.delete(self.profile_me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_me_without_token(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RBACModelsTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_permissions")

    def test_seed_roles_and_business_elements_exist(self):
        self.assertTrue(Role.objects.filter(name="admin").exists())
        self.assertTrue(Role.objects.filter(name="manager").exists())
        self.assertTrue(Role.objects.filter(name="user").exists())
        self.assertTrue(Role.objects.filter(name="guest").exists())
        self.assertTrue(BusinessElement.objects.filter(code="users").exists())
        self.assertTrue(BusinessElement.objects.filter(code="products").exists())
        self.assertTrue(BusinessElement.objects.filter(code="stores").exists())
        self.assertTrue(BusinessElement.objects.filter(code="orders").exists())
        self.assertTrue(BusinessElement.objects.filter(code="access_rules").exists())

    def test_admin_has_full_access_rule_for_users(self):
        access_rule = AccessRule.objects.get(
            role__name="admin",
            business_element__code="users",
        )

        self.assertTrue(access_rule.read_permission)
        self.assertTrue(access_rule.read_all_permission)
        self.assertTrue(access_rule.create_permission)
        self.assertTrue(access_rule.update_permission)
        self.assertTrue(access_rule.update_all_permission)
        self.assertTrue(access_rule.delete_permission)
        self.assertTrue(access_rule.delete_all_permission)

    def test_guest_has_limited_permissions(self):
        products_rule = AccessRule.objects.get(
            role__name="guest",
            business_element__code="products",
        )

        self.assertTrue(products_rule.read_permission)
        self.assertFalse(products_rule.create_permission)
        self.assertFalse(products_rule.update_permission)
        self.assertFalse(products_rule.delete_permission)

    def test_user_role_relation_is_unique(self):
        user = User.objects.create_user(
            email="rbac@example.com",
            password="strongpass123",
            first_name="Rbac",
            last_name="User",
            middle_name="Test",
        )
        role = Role.objects.get(name="user")

        UserRole.objects.create(user=user, role=role)

        with self.assertRaises(IntegrityError):
            UserRole.objects.create(user=user, role=role)

    def test_seed_command_is_idempotent(self):
        call_command("seed_roles_permissions")

        self.assertEqual(Role.objects.filter(name="admin").count(), 1)
        self.assertEqual(Role.objects.filter(name="guest").count(), 1)
        self.assertEqual(BusinessElement.objects.filter(code="orders").count(), 1)
        self.assertEqual(
            AccessRule.objects.filter(
                role__name="manager",
                business_element__code="orders",
            ).count(),
            1,
        )


class AccessPermissionServiceTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_permissions")
        self.user = User.objects.create_user(
            email="permissions@example.com",
            password="strongpass123",
            first_name="Access",
            last_name="User",
            middle_name="Test",
        )
        self.user_role = Role.objects.get(name="user")
        self.manager_role = Role.objects.get(name="manager")
        self.guest_role = Role.objects.get(name="guest")

    def test_unauthenticated_user_gets_401(self):
        with self.assertRaises(NotAuthenticated):
            check_access_permission(AnonymousUser(), "orders", "read")

    def test_user_with_role_and_permission_gets_access(self):
        UserRole.objects.create(user=self.user, role=self.user_role)

        result = check_access_permission(self.user, "orders", "create")

        self.assertTrue(result)

    def test_authenticated_user_without_permission_gets_403(self):
        UserRole.objects.create(user=self.user, role=self.guest_role)

        with self.assertRaises(PermissionDenied):
            check_access_permission(self.user, "orders", "delete")

    def test_service_supports_all_permissions(self):
        UserRole.objects.create(user=self.user, role=self.manager_role)

        result = check_access_permission(
            self.user,
            "orders",
            "read",
            check_all=True,
        )

        self.assertTrue(result)

    def test_has_access_permission_returns_false_when_no_roles(self):
        self.assertFalse(has_access_permission(self.user, "orders", "read"))

    def test_any_user_role_can_grant_access(self):
        UserRole.objects.create(user=self.user, role=self.guest_role)
        UserRole.objects.create(user=self.user, role=self.manager_role)

        self.assertTrue(
            has_access_permission(
                self.user,
                "users",
                "update",
                check_all=True,
            )
        )


class MockBusinessResourcesTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_permissions")
        self.products_url = reverse("products-list")
        self.stores_url = reverse("stores-list")
        self.orders_url = reverse("orders-list")

    def test_products_requires_authentication(self):
        response = self.client.get(self.products_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_can_view_products_and_stores(self):
        user = self._create_user_with_role("guest@example.com", "guest")

        self._authenticate(user)
        products_response = self.client.get(self.products_url)
        stores_response = self.client.get(self.stores_url)

        self.assertEqual(products_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stores_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(products_response.data["items"]), 3)
        self.assertEqual(len(stores_response.data["items"]), 2)

    def test_guest_cannot_view_orders(self):
        user = self._create_user_with_role("guest@example.com", "guest")

        self._authenticate(user)
        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_view_orders(self):
        user = self._create_user_with_role("user@example.com", "user")

        self._authenticate(user)
        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 2)

    def test_manager_can_view_all_mock_resources(self):
        user = self._create_user_with_role("manager@example.com", "manager")

        self._authenticate(user)
        products_response = self.client.get(self.products_url)
        stores_response = self.client.get(self.stores_url)
        orders_response = self.client.get(self.orders_url)

        self.assertEqual(products_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stores_response.status_code, status.HTTP_200_OK)
        self.assertEqual(orders_response.status_code, status.HTTP_200_OK)

    def _create_user_with_role(self, email, role_name):
        user = User.objects.create_user(
            email=email,
            password="strongpass123",
            first_name="Mock",
            last_name="User",
            middle_name="Test",
        )
        role = Role.objects.get(name=role_name)
        UserRole.objects.create(user=user, role=role)
        return user

    def _authenticate(self, user):
        token = create_access_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class AccessRuleAdminApiTests(APITestCase):
    def setUp(self):
        call_command("seed_roles_permissions")
        self.list_url = reverse("access-rules-list")
        self.admin_user = self._create_user_with_role("admin@example.com", "admin")
        self.manager_user = self._create_user_with_role("manager@example.com", "manager")

    def test_list_access_rules_requires_authentication(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_cannot_list_access_rules(self):
        self._authenticate(self.manager_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_access_rules(self):
        self._authenticate(self.admin_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["items"]), 0)

    def test_admin_can_update_access_rule(self):
        access_rule = AccessRule.objects.get(
            role__name="guest",
            business_element__code="products",
        )
        update_url = reverse("access-rules-update", args=[access_rule.id])

        self._authenticate(self.admin_user)
        response = self.client.patch(
            update_url,
            {"create_permission": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Access rule updated successfully.",
        )
        access_rule.refresh_from_db()
        self.assertTrue(access_rule.create_permission)

    def test_non_admin_cannot_update_access_rule(self):
        access_rule = AccessRule.objects.get(
            role__name="guest",
            business_element__code="products",
        )
        update_url = reverse("access-rules-update", args=[access_rule.id])

        self._authenticate(self.manager_user)
        response = self.client.patch(
            update_url,
            {"create_permission": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _create_user_with_role(self, email, role_name):
        user = User.objects.create_user(
            email=email,
            password="strongpass123",
            first_name="Admin",
            last_name="Api",
            middle_name="Test",
        )
        role = Role.objects.get(name=role_name)
        UserRole.objects.create(user=user, role=role)
        return user

    def _authenticate(self, user):
        token = create_access_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
