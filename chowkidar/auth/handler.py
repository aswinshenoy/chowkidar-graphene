from datetime import datetime
from django.http import HttpRequest, JsonResponse
from django.utils import timezone

from .fingerprint import generate_fingerprint_from_request, decode_fingerprint
from ..models import RefreshToken
from ..settings import (
    JWT_REFRESH_TOKEN_EXPIRATION_DELTA,
    JWT_EXPIRATION_DELTA,
    UPDATE_USER_LAST_LOGIN_ON_AUTH,
    UPDATE_USER_LAST_LOGIN_ON_REFRESH
)
from ..utils import generate_refresh_token, generate_token_from_claims, decode_payload_from_token
from ..utils.cookie import set_cookie, delete_cookie


def clear_cookies(resp: JsonResponse) -> JsonResponse:
    resp = delete_cookie(key='JWT_REFRESH_TOKEN', response=resp)
    resp = delete_cookie(key='JWT_TOKEN', response=resp)
    return resp


def logout_user(request: HttpRequest, result: object, status_code: str) -> JsonResponse:
    if 'JWT_REFRESH_TOKEN' in request.COOKIES:
        refreshToken = request.COOKIES["JWT_REFRESH_TOKEN"]
        try:
            # Revoke refresh token
            token = RefreshToken.objects.get(token=refreshToken)
            token.revoked = timezone.now()
            token.save()
        except Exception:
            pass
        return clear_cookies(JsonResponse(result, status=status_code))


def update_user_last_login(user, isLogin=False, isRefresh=False):
    if isLogin and UPDATE_USER_LAST_LOGIN_ON_AUTH:
        user.last_login = timezone.now()
        user.save()
    if isRefresh and UPDATE_USER_LAST_LOGIN_ON_REFRESH:
        user.last_login = timezone.now()
        user.save()


def is_auth_result(result: object) -> bool:
    return (
        # Password Auth
        (
            'authenticateUser' in result['data'] and
            result['data']['authenticateUser'] and
            'success' in result['data']['authenticateUser'] and
            result['data']['authenticateUser']['success'] and
            result['data']['authenticateUser']['user']['id']
        ) or
        # Social Auth
        (
            'socialAuth' in result['data'] and
            'success' in result['data']['socialAuth'] and
            result['data']['socialAuth']['success'] and
            result['data']['socialAuth']['user']['id']
        )
    )


def respond_handling_authentication(
    request: HttpRequest, result: object, status_code: str
) -> JsonResponse:
    if status_code == 200 and result['data']:

        # Issue Token if query is authenticateUser and successful
        if is_auth_result(result):
            if 'socialAuth' in result['data'] and result['data']['socialAuth']['success']:
                user = result['data']['socialAuth']['user']
                userID = user['id']
            else:
                user = result['data']['authenticateUser']['user']
                userID = user['id']

            rt = generate_refresh_token(userID=userID, request=request)
            update_user_last_login(rt.user, isLogin=True)

            fingerprint = generate_fingerprint_from_request(request)
            decoded = decode_fingerprint(fingerprint)
            data = generate_token_from_claims(
                claims={
                    'refreshToken': rt.get_token(),
                    'fingerprint': fingerprint,
                    'ip': decoded['ip'],
                    'userAgent': decoded['agent']
                },
                expirationDelta=JWT_REFRESH_TOKEN_EXPIRATION_DELTA
            )
            refreshExpiresIn = datetime.fromtimestamp(data['payload']['exp'])
            if 'socialAuth' in result['data'] and result['data']['socialAuth']['success']:
                result['data']['socialAuth']['refreshExpiresIn'] = refreshExpiresIn
            else:
                result['data']['authenticateUser']['refreshExpiresIn'] = refreshExpiresIn
            resp = JsonResponse(result, status=status_code)

            # Set JWT Refresh Token
            resp = set_cookie(
                key='JWT_REFRESH_TOKEN', value=data['token'],
                expires=refreshExpiresIn, response=resp
            )
            return resp

        # Revoke Token if query is logoutUser and successful
        if 'logoutUser' in result['data'] and result['data']['logoutUser']:
            logout_user(request=request, result=result, status_code=status_code)

    # Refresh Token automatically if token exists
    if 'JWT_REFRESH_TOKEN' in request.COOKIES:
        refreshToken = request.COOKIES["JWT_REFRESH_TOKEN"]
        if 'JWT_TOKEN' in request.COOKIES:
            token = request.COOKIES['JWT_TOKEN']
            try:
                payload = decode_payload_from_token(token=token)
                expiry = datetime.fromtimestamp(payload['exp'])
                now = datetime.now()
                if expiry > now + (JWT_EXPIRATION_DELTA/2):
                    resp = JsonResponse(result, status=status_code)
                    return resp
            except Exception:
                # Generate new token using refresh token
                pass
        from .verify import verify_refresh_token
        try:
            resp = JsonResponse(result, status=status_code)

            # verify and get refresh token. Will throw exceptions if token is invalid
            rt = verify_refresh_token(refreshToken)

            # Generate fingerprint for current request
            fingerprint = generate_fingerprint_from_request(request)
            decoded = decode_fingerprint(fingerprint)

            # Check if fingerprint has changed due to IP or agent
            # If changed, issue a new refresh token invalidating the old one
            if (
                rt.userAgent != decoded['agent']  # User Agent has changed
                or rt.ip != decoded['ip']  # IP has changed
            ):
                # Revoke the old token
                rt.revoked = timezone.now()
                rt.save()

                # Issue new refresh token
                newToken = RefreshToken.objects.create(
                    user=rt.user,
                    ip=decoded['ip'],
                    userAgent=decoded['agent']
                )
                data = generate_token_from_claims(
                    claims={
                        'refreshToken': newToken.get_token(),
                        'fingerprint': fingerprint,
                        'ip': decoded['ip'],
                        'userAgent': decoded['agent']
                    },
                    expirationDelta=JWT_REFRESH_TOKEN_EXPIRATION_DELTA
                )
                refreshExpiresIn = datetime.fromtimestamp(data['payload']['exp'])
                resp = set_cookie(
                    key='JWT_REFRESH_TOKEN', value=data['token'],
                    expires=refreshExpiresIn, response=resp
                )

            update_user_last_login(rt.user, isRefresh=True)

            # Generate and set new JWT_AUTH_TOKEN
            data = generate_token_from_claims(
                claims={
                    'userID': rt.user.id,
                    'username': rt.user.username,
                    'origIat': rt.issued.timestamp()
                },
                expirationDelta=JWT_EXPIRATION_DELTA
            )
            JWTExpiry = datetime.fromtimestamp(data['payload']['exp'])
            resp = set_cookie(
                key='JWT_TOKEN', value=data['token'],
                expires=JWTExpiry, response=resp
            )

            return resp
        except Exception as e:
            return clear_cookies(JsonResponse(result, status=status_code))

    return JsonResponse(result, status=status_code)


__all__ = [
    'respond_handling_authentication'
]

