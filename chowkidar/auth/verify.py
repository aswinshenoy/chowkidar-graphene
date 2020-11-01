from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import RefreshToken
from ..settings import JWT_REFRESH_TOKEN_EXPIRATION_DELTA
from ..utils import decode_payload_from_token, AuthError

UserModel = get_user_model()


def resolve_user_from_tokens(token=None, refreshToken=None) -> str:
    if token:
        try:
            payload = decode_payload_from_token(token=token)
            try:
                return payload['userID']
            except Exception:
                pass
        except Exception:
            pass
    if refreshToken:
        try:
            refreshToken = verify_refresh_token(token=refreshToken)
            return refreshToken.user.id
        except Exception:
            pass
    return None


def resolve_user_from_request(request: HttpRequest) -> str:
    return resolve_user_from_tokens(
        token=request.COOKIES["JWT_TOKEN"] if 'JWT_TOKEN' in request.COOKIES else None,
        refreshToken=request.COOKIES["JWT_REFRESH_TOKEN"] if 'JWT_REFRESH_TOKEN' in request.COOKIES else None
    )


def verify_refresh_token(token: str) -> RefreshToken:
    try:
        token = RefreshToken.objects.get(token=token, revoked__isnull=True)
        if timezone.now() > token.issued + JWT_REFRESH_TOKEN_EXPIRATION_DELTA:
            raise AuthError('Refresh Token Expired', code='EXPIRED_REFRESH_TOKEN')
        return token
    except RefreshToken.DoesNotExist:
        raise AuthError('Invalid Refresh Token', code='INVALID_REFRESH_TOKEN')


__all__ = [
    'verify_refresh_token',
    'resolve_user_from_tokens',
    'resolve_user_from_request',
]
