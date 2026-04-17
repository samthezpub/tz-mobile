from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone


ACCESS_TOKEN_LIFETIME = timedelta(hours=1)
ALGORITHM = "HS256"


def create_access_token(user):
    now = timezone.now()
    payload = {
        "user_id": user.id,
        "iat": int(now.timestamp()),
        "exp": int((now + ACCESS_TOKEN_LIFETIME).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as error:
        raise ValueError("Token has expired.") from error
    except jwt.InvalidTokenError as error:
        raise ValueError("Token is invalid.") from error
