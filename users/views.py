from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer, UserSerializer


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
