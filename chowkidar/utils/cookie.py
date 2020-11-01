from datetime import datetime
from django.http import HttpResponse,JsonResponse


def set_cookie(
    key: str,
    value: str,
    response: (HttpResponse or JsonResponse),
    expires: datetime,
) -> (HttpResponse or JsonResponse):
    """ Sets a cookie through HTTP Response """
    response.set_cookie(
        key=key,
        value=value,
        # if enabled, cookie is sent only when request is made via https
        secure=False,
        # prevents client-side JS from accessing cookie
        httponly=True,
        # expire time of cookie
        expires=expires
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
