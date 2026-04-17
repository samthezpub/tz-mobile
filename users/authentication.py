from rest_framework import authentication, exceptions

from users.models import User
from users.tokens import decode_access_token


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]

        try:
            payload = decode_access_token(token)
        except ValueError as error:
            raise exceptions.AuthenticationFailed(str(error))

        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token payload is invalid.")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found.")

        return (user, token)
