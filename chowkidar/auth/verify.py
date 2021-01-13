from typing import Optional

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.utils import timezone

from .fingerprint import decode_fingerprint
from ..models import RefreshToken
from ..settings import JWT_REFRESH_TOKEN_EXPIRATION_DELTA
from ..utils import decode_payload_from_token, AuthError

UserModel = get_user_model()


def resolve_user_from_tokens(token=None, refreshToken=None) -> Optional[str]:
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
    payload = decode_payload_from_token(token=token)
    if "fingerprint" in payload:
        fingerprintDecode = decode_fingerprint(payload['fingerprint'])
        if (
            fingerprintDecode['ip'] == payload['ip'] and
            fingerprintDecode['agent'] == payload['userAgent']
        ):
            token = RefreshToken.objects.get(
                token=payload['refreshToken'],
                revoked__isnull=True  # A refresh token is revoked if the revoked timestamp is set
            )
            if (
                # Check if the ip & user agents in payload match those in db
                token.ip == payload['ip'] and
                token.userAgent == payload['userAgent'] and
                # Check if the token has not expired
                token.issued + JWT_REFRESH_TOKEN_EXPIRATION_DELTA > timezone.now()
            ):
                # Check if the token has not expired
                if token.issued + JWT_REFRESH_TOKEN_EXPIRATION_DELTA > timezone.now():
                    return token
                raise AuthError('Refresh token validity expired', code='REFRESH_TOKEN_EXPIRED')
            raise AuthError('Refresh token payload not matching records', code='INVALID_TOKEN_PAYLOAD')
    raise AuthError('Invalid fingerprint for refresh token', code='INVALID_REFRESH_TOKEN_FINGERPRINT')


def get_refresh_token_from_request(request: HttpRequest) -> RefreshToken:
    if 'JWT_REFRESH_TOKEN' in request.COOKIES:
        return verify_refresh_token(token=request.COOKIES["JWT_REFRESH_TOKEN"])
    raise AuthError('Refresh Token Missing', code='REFRESH_TOKEN_NOT_FOUND')


__all__ = [
    'verify_refresh_token',
    'get_refresh_token_from_request',
    'resolve_user_from_tokens',
    'resolve_user_from_request',
]
