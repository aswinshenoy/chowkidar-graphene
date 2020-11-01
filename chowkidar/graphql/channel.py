from http.cookies import SimpleCookie

from channels.auth import UserLazyObject
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.contrib.auth.models import AnonymousUser

from user.models import User
from ..auth.verify import resolve_user_from_tokens


class ChannelAuthMiddleware(BaseMiddleware):
    def populate_scope(self, scope):
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    @database_sync_to_async
    def resolve_user(self, cookie):
        userID = resolve_user_from_tokens(
            token=cookie['JWT_TOKEN'].value if 'JWT_TOKEN' in cookie else None,
            refreshToken=cookie['JWT_REFRESH_TOKEN'].value if 'JWT_REFRESH_TOKEN' in cookie else None
        )
        if userID:
            try:
                return User.objects.get(id=userID)
            except User.DoesNotExist:
                pass
        return AnonymousUser()

    async def resolve_scope(self, scope):
        headers = dict(scope['headers'])
        user = AnonymousUser()
        if b'cookie' in headers:
            cookie = SimpleCookie()
            cookie.load(str(headers[b'cookie']))
            user = await self.resolve_user(cookie)
        scope["user"]._wrapped = user


__all__ = [
    'ChannelAuthMiddleware'
]
