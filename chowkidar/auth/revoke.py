from django.utils import timezone

from ..models import RefreshToken


def revoke_refresh_token(token):
    try:
        token = RefreshToken.objects.get(token=token)
        token.revoked = timezone.now()
        token.save()
    except RefreshToken.DoesNotExist:
        raise Exception('Token Does not exist')


__all__ = [
    'revoke_refresh_token'
]
