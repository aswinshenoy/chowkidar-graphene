from datetime import timedelta
from django.conf import settings


JWT_SECRET_KEY = settings.JWT_SECRET_KEY if hasattr(settings, 'JWT_SECRET_KEY') else settings.SECRET_KEY
JWT_PUBLIC_KEY = settings.JWT_PUBLIC_KEY if hasattr(settings, 'JWT_PUBLIC_KEY') else None
JWT_PRIVATE_KEY = settings.JWT_PRIVATE_KEY if hasattr(settings, 'JWT_PRIVATE_KEY') else None
JWT_REFRESH_TOKEN_N_BYTES = settings.JWT_REFRESH_TOKEN_N_BYTES if hasattr(settings, 'JWT_REFRESH_TOKEN_N_BYTES') else 20
JWT_ALGORITHM = settings.JWT_ALGORITHM if hasattr(settings, 'JWT_ALGORITHM') else 'HS256'
JWT_EXPIRATION_DELTA = (
    settings.JWT_EXPIRATION_DELTA if hasattr(settings, 'JWT_EXPIRATION_DELTA') else timedelta(seconds=60 * 5)
)
JWT_REFRESH_TOKEN_EXPIRATION_DELTA = (
    settings.JWT_REFRESH_TOKEN_EXPIRATION_DELTA if hasattr(settings, 'JWT_REFRESH_TOKEN_EXPIRATION_DELTA')
    else timedelta(seconds=60 * 60 * 24 * 7)
)
JWT_LEEWAY = settings.JWT_LEEWAY if hasattr(settings, 'JWT_LEEWAY') else 0
JWT_ISSUER = settings.JWT_ISSUER if hasattr(settings, 'JWT_ISSUER') else None
