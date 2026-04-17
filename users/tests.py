from django.db import IntegrityError
from django.urls import reverse
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
    def test_seed_roles_and_business_elements_exist(self):
        self.assertTrue(Role.objects.filter(name="admin").exists())
        self.assertTrue(Role.objects.filter(name="manager").exists())
        self.assertTrue(Role.objects.filter(name="user").exists())
        self.assertTrue(BusinessElement.objects.filter(code="profile").exists())
        self.assertTrue(BusinessElement.objects.filter(code="users").exists())

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
