from .verify import resolve_user_from_request


class ChowkidarAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        context = info.context
        userID = resolve_user_from_request(context)
        context.userID = userID
        return next(root, info, **kwargs)


__all__ = [
    'ChowkidarAuthMiddleware'
]
