from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


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

    def test_get_me_without_token(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
