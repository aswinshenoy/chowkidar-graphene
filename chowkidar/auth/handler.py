from django.utils import timezone
from datetime import datetime
from django.http import HttpRequest, JsonResponse

from .revoke import revoke_refresh_token
from ..settings import (
    JWT_REFRESH_TOKEN_EXPIRATION_DELTA,
    JWT_EXPIRATION_DELTA,
    UPDATE_USER_LAST_LOGIN_ON_AUTH,
    UPDATE_USER_LAST_LOGIN_ON_HARD_REFRESH
)
from ..utils import generate_refresh_token, generate_token_from_claims, decode_payload_from_token
from ..utils.cookie import set_cookie, delete_cookie


def respond_handling_authentication(
    request: HttpRequest, result: object, status_code
) -> JsonResponse:
    if status_code == 200 and result['data']:
        # Issue Token if query is authenticateUser and successful
        if (
            (
                'authenticateUser' in result['data'] and
                result['data']['authenticateUser'] and
                'success' in result['data']['authenticateUser'] and
                result['data']['authenticateUser']['success'] and
                result['data']['authenticateUser']['user']['id']
            ) or
            (
                'socialAuth' in result['data'] and
                'success' in result['data']['socialAuth'] and
                result['data']['socialAuth']['success'] and
                result['data']['socialAuth']['user']['id']
            )
        ):
            if 'socialAuth' in result['data'] and result['data']['socialAuth']['success']:
                user = result['data']['socialAuth']['user']
                userID = user['id']
            else:
                user = result['data']['authenticateUser']['user']
                userID = user['id']
            refreshToken = generate_refresh_token(userID=userID)

            if UPDATE_USER_LAST_LOGIN_ON_AUTH:
                u = refreshToken.user
                u.last_login = refreshToken.issued
                u.save()

            data = generate_token_from_claims(claims={
                'userID': userID, 'username': user['username'], 'origIat': refreshToken.issued.timestamp(),
            })
            refreshExpiresIn = timezone.now() + JWT_REFRESH_TOKEN_EXPIRATION_DELTA
            if 'socialAuth' in result['data'] and result['data']['socialAuth']['success']:
                result['data']['socialAuth']['payload'] = data['payload']
                result['data']['socialAuth']['refreshExpiresIn'] = refreshExpiresIn
            else:
                result['data']['authenticateUser']['payload'] = data['payload']
                result['data']['authenticateUser']['refreshExpiresIn'] = refreshExpiresIn
            resp = JsonResponse(result, status=status_code)

            # Set JWT Token on signup is disabled at the moment
            # JWTExpiry = datetime.fromtimestamp(data['payload']['exp'])
            # resp = set_cookie(
            #     key='JWT_TOKEN',
            #     value=data['token'],
            #     expires=JWTExpiry,
            #     response=resp
            # )
            # Set JWT Refresh Token
            resp = set_cookie(
                key='JWT_REFRESH_TOKEN',
                value=refreshToken.get_token(),
                expires=refreshExpiresIn,
                response=resp
            )
            return resp
        # Revoke Token if query is logoutUser and successful
        if (
            'logoutUser' in result['data'] and
            result['data']['logoutUser']
        ):
            if 'JWT_REFRESH_TOKEN' in request.COOKIES:
                refreshToken = request.COOKIES["JWT_REFRESH_TOKEN"]
                try:
                    revoke_refresh_token(refreshToken)
                except Exception:
                    pass
                resp = JsonResponse(result, status=status_code)
                resp = delete_cookie(key='JWT_REFRESH_TOKEN', response=resp)
                resp = delete_cookie(key='JWT_TOKEN', response=resp)
                return resp

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
                pass
        from .verify import verify_refresh_token
        try:
            rt = verify_refresh_token(refreshToken)

            if UPDATE_USER_LAST_LOGIN_ON_HARD_REFRESH:
                u = rt.user
                u.last_login = rt.issued
                u.save()

            data = generate_token_from_claims(claims={
                'userID': rt.user.id, 'username': rt.user.username, 'origIat': rt.issued.timestamp(),
            })
            JWTExpiry = datetime.fromtimestamp(data['payload']['exp'])
            resp = JsonResponse(result, status=status_code)
            resp = set_cookie(
                key='JWT_TOKEN', value=data['token'],
                expires=JWTExpiry, response=resp
            )
            return resp
        except Exception:
            resp = JsonResponse(result, status=status_code)
            resp = delete_cookie(key='JWT_REFRESH_TOKEN', response=resp)
            resp = delete_cookie(key='JWT_TOKEN', response=resp)
            return resp

    return JsonResponse(result, status=status_code)


__all__ = [
    'respond_handling_authentication'
]

