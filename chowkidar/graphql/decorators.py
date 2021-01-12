from django.contrib.auth import get_user_model

from ..auth.verify import get_refresh_token_from_request
from ..utils.exceptions import PermissionDenied

User = get_user_model()


def login_required(resolver):
    """ Checks JWT Auth Token & resolves info.context.userID """
    def wrapper(parent, info, *args, **kwargs):
        userID = getattr(info.context, "userID", None)
        if userID:
            info.context.userID = userID
            return resolver(parent, info, *args, **kwargs)
        raise PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')
    return wrapper


def fingerprint_required(resolver):
    """
        Checks JWT Refresh Token, verifies it against db & resolves info.context.userID and info.context.refreshToken
    """
    def wrapper(parent, info, *args, **kwargs):
        userID = getattr(info.context, "userID", None)
        if userID:
            request = info.context
            refreshToken = get_refresh_token_from_request(request)
            info.context.userID = userID
            info.context.refreshToken = refreshToken
            return resolver(parent, info, *args, **kwargs)
        raise PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')
    return wrapper


def resolve_user(resolver):
    """ Checks JWT Auth Token & resolves info.context.user with User object hitting the db """
    def wrapper(parent, info, *args, **kwargs):
        userID = getattr(info.context, "userID", None)
        if userID:
            try:
                info.context.user = User.objects.get(id=userID)
                info.context.userID = userID
                return resolver(parent, info, *args, **kwargs)
            except User.DoesNotExist:
                pass
        raise PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')
    return wrapper


__all__ = [
    'login_required',
    'fingerprint_required',
    'resolve_user',
]
