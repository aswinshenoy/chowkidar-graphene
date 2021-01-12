from datetime import timedelta
from django.conf import settings


JWT_SECRET_KEY = settings.JWT_SECRET_KEY if hasattr(settings, 'JWT_SECRET_KEY') else settings.SECRET_KEY
JWT_PUBLIC_KEY = settings.JWT_PUBLIC_KEY if hasattr(settings, 'JWT_PUBLIC_KEY') else None
JWT_PRIVATE_KEY = settings.JWT_PRIVATE_KEY if hasattr(settings, 'JWT_PRIVATE_KEY') else None
JWT_REFRESH_TOKEN_N_BYTES = settings.JWT_REFRESH_TOKEN_N_BYTES if hasattr(settings, 'JWT_REFRESH_TOKEN_N_BYTES') else 20
JWT_ALGORITHM = settings.JWT_ALGORITHM if hasattr(settings, 'JWT_ALGORITHM') else 'HS256'
JWT_LEEWAY = settings.JWT_LEEWAY if hasattr(settings, 'JWT_LEEWAY') else 0
JWT_ISSUER = settings.JWT_ISSUER if hasattr(settings, 'JWT_ISSUER') else None
JWT_EXPIRATION_DELTA = (
    settings.JWT_EXPIRATION_DELTA if hasattr(settings, 'JWT_EXPIRATION_DELTA') else timedelta(seconds=60)
)
JWT_REFRESH_TOKEN_EXPIRATION_DELTA = (
    settings.JWT_REFRESH_TOKEN_EXPIRATION_DELTA if hasattr(settings, 'JWT_REFRESH_TOKEN_EXPIRATION_DELTA')
    else timedelta(seconds=60 * 60 * 24 * 7)
)
ALLOW_USER_TO_LOGIN_ON_AUTH = (
    settings.ALLOW_USER_TO_LOGIN_ON_AUTH if hasattr(settings, 'ALLOW_USER_TO_LOGIN_ON_AUTH')
    else 'chowkidar.auth.rules.check_if_user_is_allowed_to_login'
)
REVOKE_OTHER_TOKENS_ON_AUTH_FOR_USER = (
    settings.REVOKE_OTHER_TOKENS_ON_AUTH_FOR_USER if hasattr(settings, 'REVOKE_OTHER_TOKENS_ON_AUTH_FOR_USER')
    else 'chowkidar.auth.rules.check_if_other_tokens_need_to_be_revoked'
)
UPDATE_USER_LAST_LOGIN_ON_AUTH = (
    settings.UPDATE_USER_LAST_LOGIN_ON_AUTH if hasattr(settings, 'UPDATE_USER_LAST_LOGIN_ON_AUTH')
    else True
)
UPDATE_USER_LAST_LOGIN_ON_REFRESH = (
    settings.UPDATE_USER_LAST_LOGIN_ON_AUTH if hasattr(settings, 'UPDATE_USER_LAST_LOGIN_ON_REFRESH')
    else True
)
LOG_USER_IP_IN_REFRESH_TOKEN = (
    settings.LOG_USER_IP_IN_REFRESH_TOKEN if hasattr(settings, 'LOG_USER_IP_IN_REFRESH_TOKEN')
    else True
)
LOG_USER_AGENT_IN_REFRESH_TOKEN = (
    settings.LOG_USER_AGENT_IN_REFRESH_TOKEN if hasattr(settings, 'LOG_USER_AGENT_IN_REFRESH_TOKEN')
    else True
)
USER_GRAPHENE_OBJECT = (
    settings.USER_GRAPHENE_OBJECT if hasattr(settings, 'UPDATE_USER_LAST_LOGIN_ON_REFRESH')
    else 'user.graphql.types.user.PersonalProfile'
)
