import binascii
import os

from django.db import models
from django.conf import settings
from chowkidar.settings import JWT_REFRESH_TOKEN_N_BYTES


class AbstractRefreshToken(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refresh_token',
        editable=False
    )
    token = models.CharField(max_length=255, editable=False)
    issued = models.DateTimeField(auto_now_add=True, editable=False)
    revoked = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def generate_token():
        return binascii.hexlify(os.urandom(JWT_REFRESH_TOKEN_N_BYTES)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self._cached_token = self.generate_token()
        super().save(*args, **kwargs)

    def get_token(self):
        if hasattr(self, '_cached_token'):
            return self._cached_token
        return self.token

    class Meta:
        abstract = True
        # (token, revoked) ensures uniqueness of non-revoked tokens (since revoked=null)
        unique_together = ('token', 'revoked')

    def __str__(self):
        return self.token


class RefreshToken(AbstractRefreshToken):
    """ RefreshToken default model """


__all__ = [
    'RefreshToken'
]
