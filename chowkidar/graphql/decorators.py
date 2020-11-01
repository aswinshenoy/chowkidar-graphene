from user.models import User
from ..utils import exceptions


def login_required(resolver):
    def wrapper(parent, info, *args, **kwargs):
        userID = getattr(info.context, "userID", None)
        if userID:
            info.context.userID = userID
            resolved = resolver(parent, info, *args, **kwargs)
            return resolved
        raise exceptions.PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')
    return wrapper


def resolve_user(resolver):
    def wrapper(parent, info, *args, **kwargs):
        userID = getattr(info.context, "userID", None)
        if userID:
            try:
                info.context.user = User.objects.get(id=userID)
                info.context.userID = userID
                resolved = resolver(parent, info, *args, **kwargs)
                return resolved
            except User.DoesNotExist:
                pass
        raise exceptions.PermissionDenied(message='User not authenticated', code='AUTHENTICATION_REQUIRED')
    return wrapper


__all__ = [
    'login_required',
    'resolve_user',
]
