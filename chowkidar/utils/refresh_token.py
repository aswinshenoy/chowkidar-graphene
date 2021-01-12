from django.contrib.auth import get_user_model
from django.http import HttpRequest

from chowkidar.auth.fingerprint import get_user_ip_from_request, get_user_agent_from_request
from chowkidar.models import RefreshToken
from chowkidar.settings import LOG_USER_IP_IN_REFRESH_TOKEN, LOG_USER_AGENT_IN_REFRESH_TOKEN

UserModel = get_user_model()


def generate_refresh_token(userID: str, request: HttpRequest) -> RefreshToken:
    agent = None
    if LOG_USER_AGENT_IN_REFRESH_TOKEN:
        agent = get_user_agent_from_request(request)
    ip = None
    if LOG_USER_IP_IN_REFRESH_TOKEN:
        ip = get_user_ip_from_request(request)
    return RefreshToken.objects.create(user_id=userID, ip=ip, userAgent=agent)


__all__ = [
    'generate_refresh_token'
]
