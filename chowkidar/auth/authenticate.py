import re

from typing import Union
from django.contrib.auth import authenticate, get_user_model
from django.http import HttpRequest

from ..utils.exceptions import AuthError

UserModel = get_user_model()


def validate_email(email: str) -> str:
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        raise AuthError(message='You have entered an invalid email address', code='INVALID_EMAIL')
    return email


def authenticate_with_username(password: str, username: str, request: HttpRequest = None) -> Union[UserModel, None]:
    return authenticate(request=request, username=username, password=password)


def authenticate_with_email(password: str, email: str, request: HttpRequest = None):
    try:
        username = UserModel.objects.get(email=validate_email(email)).username
        return authenticate_with_username(password=password, username=username, request=request)
    except UserModel.DoesNotExist:
        raise AuthError(message='An account with this email address does not exist', code='EMAIL_NOT_FOUND')
    except UserModel.MultipleObjectsReturned:
        raise AuthError(
            message='We cannot authenticate you with your email address, please enter your username',
            code='EMAIL_NOT_UNIQUE'
        )


def authenticate_user_from_credentials(
    password: str, username: str = None, email: str = None, request: HttpRequest = None
) -> UserModel:
    if username is None:
        if email is not None:
            user = authenticate_with_email(email=email, password=password, request=request)
        else:
            raise AuthError(message='Email or username is required for authentication', code='EMAIL_USERNAME_MISSING')
    else:
        user = authenticate_with_username(username=username, password=password, request=request)
    if user is None:
        msg = 'The username or password you entered is wrong'
        if username is None:
            msg = 'The email or password you entered is wrong'
        raise AuthError(message=msg, code='INVALID_CREDENTIALS')
    return user


__all__ = [
    'authenticate_user_from_credentials',
]
