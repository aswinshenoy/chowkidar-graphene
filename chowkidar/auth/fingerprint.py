from ipware import get_client_ip
from django.core import signing
from chowkidar.utils import decode_payload_from_token, AuthError, PermissionDenied


def get_user_ip_from_request(request) -> str:
    clientIP, is_routable = get_client_ip(request)
    if clientIP is None:
        raise AuthError("Cannot retrieve user's IP Address", code='IP_MISSING')
    return str(clientIP)


def get_user_agent_from_request(request):
    if 'User-Agent' in request.headers:
        return request.headers['user-agent']


def encode_fingerprint(ip, agent):
    return signing.dumps({"ip": ip,  "agent": agent})


def decode_fingerprint(fingerprint) -> object:
    return signing.loads(fingerprint)


def decode_fingerprint_from_request(request):
    try:
        if 'JWT_REFRESH_TOKEN' in request.COOKIES:
            payload = decode_payload_from_token(token=request.COOKIES["JWT_REFRESH_TOKEN"])
            if "fingerprint" in payload:
                return decode_fingerprint(payload['fingerprint'])
    except Exception:
        pass
    raise PermissionDenied('Failed to decode Fingerprint', code='INVALID_FINGERPRINT')


def generate_fingerprint_from_request(request) -> str:
    agent = get_user_agent_from_request(request)
    ip = get_user_ip_from_request(request)
    return encode_fingerprint(ip=ip, agent=agent)


__all__ = [
    'get_user_ip_from_request',
    'get_user_agent_from_request',
    'encode_fingerprint',
    'decode_fingerprint',
    'decode_fingerprint_from_request',
    'generate_fingerprint_from_request'
]
