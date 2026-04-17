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
