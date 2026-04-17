from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserBriefSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)
from users.services import blacklist_token
from users.tokens import create_access_token


class UsersHealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "users"})


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = create_access_token(user)

        return Response(
            {
                "token": token,
                "user": UserBriefSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        blacklist_token(request.user, request.auth)
        return Response(
            {"message": "Logout successful."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": UserSerializer(request.user).data})

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profile updated successfully.",
                "user": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        blacklist_token(request.user, request.auth)
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])

        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_200_OK,
        )
