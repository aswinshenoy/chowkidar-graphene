from datetime import datetime

import jwt

from ..settings import (
    JWT_EXPIRATION_DELTA,
    JWT_ISSUER,
    JWT_ALGORITHM,
    JWT_PRIVATE_KEY,
    JWT_SECRET_KEY,
    JWT_PUBLIC_KEY,
    JWT_LEEWAY
)

from .exceptions import AuthError


def generate_payload_from_claims(claims: dict) -> dict:
    """
    Generates payload for creating JWT token including a dict of claims passed-in
    :param claims: a dict with claims for the JWT
    :return: a dict with payload for generating the JWT
    """
    now = datetime.utcnow()
    payload = dict()
    payload.update(claims)
    registeredClaims = {
        # Registered Claims
        # issued at
        'iat': now,
        # expiration time
        'exp': now + JWT_EXPIRATION_DELTA,
    }
    if JWT_ISSUER is not None:
        registeredClaims['iss'] = JWT_ISSUER
    payload.update(registeredClaims)
    return payload


def encode_payload(payload: object) -> str:
    return jwt.encode(
        # payload
        payload,
        # private key or secret key
        JWT_PRIVATE_KEY or JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    ).decode('utf-8')


def decode_token(token: str) -> object:
    return jwt.decode(
        token,
        # public key or secret key
        key=JWT_PUBLIC_KEY or JWT_SECRET_KEY,
        verify=True,
        algorithms=[JWT_ALGORITHM],
        # time margin in seconds for the expiration check
        leeyway=JWT_LEEWAY,
        options={
            'require_iat': True,
            'require_exp': True,
            'verify_iat': True,
            'verify_exp': True,
        },
        issuer=JWT_ISSUER,
    )


def generate_token_from_claims(claims: dict) -> object:
    payload = generate_payload_from_claims(claims)
    return {"token": encode_payload(payload), "payload": payload}


def decode_payload_from_token(token: str) -> object:
    try:
        payload = decode_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError('EXPIRED_TOKEN')
    except jwt.InvalidTokenError:
        raise AuthError('INVALID_TOKEN')


__all__ = [
    'generate_token_from_claims',
    'decode_payload_from_token'
]
