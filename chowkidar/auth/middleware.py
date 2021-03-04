from .verify import resolve_user_from_request


class ChowkidarAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        context = info.context
        if not hasattr(info.context, 'ChowkidarIDResolved'):
            userID = resolve_user_from_request(context)
            info.context.userID = userID
            info.context.ChowkidarIDResolved = True
        return next(root, info, **kwargs)


__all__ = [
    'ChowkidarAuthMiddleware'
]
