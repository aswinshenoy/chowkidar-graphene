from datetime import datetime
from django.http import HttpResponse, JsonResponse


def set_cookie(
    key: str,
    value: str,
    response: (HttpResponse or JsonResponse),
    expires: datetime,
) -> (HttpResponse or JsonResponse):
    """ Sets a cookie through HTTP Response """
    from ..settings import JWT_COOKIE_SAME_SITE, JWT_COOKIE_SECURE, JWT_COOKIE_HTTP_ONLY, JWT_COOKIE_DOMAIN

    response.set_cookie(
        key=key,
        value=value,
        # if enabled, cookie is sent only when request is made via https
        secure=JWT_COOKIE_SECURE,
        # prevents client-side JS from accessing cookie
        httponly=JWT_COOKIE_HTTP_ONLY,
        # expire time of cookie
        expires=expires,
        # same site disable
        samesite=JWT_COOKIE_SAME_SITE,
        # cookie domain
        domain=JWT_COOKIE_DOMAIN
    )
    return response


def delete_cookie(
    key: str,
    response: (HttpResponse or JsonResponse),
) -> (HttpResponse or JsonResponse):
    """ Deletes a cookie through HTTP Response """
    response.delete_cookie(key=key)
    return response


__all__ = [
    'set_cookie',
    'delete_cookie'
]
