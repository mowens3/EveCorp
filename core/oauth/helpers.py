"""Collection of various helper methods for OAuth 2.0, encoding and etc
"""

import base64
import os
import re
import hashlib
from jose import ExpiredSignatureError

from core.oauth.jwt_validator import JWTValidator

ENCODING = "utf-8"
CODE_VERIFIER_RAW = 64


def gen_code_verifier() -> str:
    """Generates code verifier
    :return: code verifier
    """
    tmp = base64.urlsafe_b64encode(os.urandom(CODE_VERIFIER_RAW)).decode(ENCODING)
    code_verifier = re.sub("[^a-zA-Z\\d]+", "", tmp)
    return code_verifier


def gen_code_challenge(code_verifier) -> str:
    """Generates code challenge based on code verifier
    :param code_verifier:
    :return: code challenge
    """
    code_challenge = hashlib.sha256(code_verifier.encode(ENCODING)).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode(ENCODING)
    code_challenge = code_challenge.replace("=", "")
    return code_challenge


def get_authorization_header_value(client_id, client_secret) -> str:
    """Generates Authorization header for ESI requests
    :param client_id: app Client ID
    :param client_secret: app Client Secret
    :return: Authorization header value
    """
    _bytes = ":".join([client_id, client_secret]).encode(ENCODING)
    encoded = base64.standard_b64encode(_bytes)
    authorization = "".join(["Basic ", encoded.decode(ENCODING)])
    return authorization


def validate(access_token) -> tuple:
    """Additional processing for Access Token contents which extracts EVE Online Character ID and name
    :param access_token: OAuth 2.0 Access Token from ESI
    :return: 2 values tuple with character id and name
    """
    tenant = None
    sub = None
    name = None
    try:
        tenant, sub, name = JWTValidator.validate(access_token)
    except ExpiredSignatureError:
        pass
    character_id = extract_character_id(sub)
    character_name = name
    return character_id, character_name


def extract_character_id(sub) -> int:
    """Extracts EVE Online Character ID from AccessToken 'sub' value
    :param sub: AccessToken 'sub' value
    :return: Character ID
    """
    return int(sub.replace("CHARACTER:EVE:", "")) if sub is not None else 0


def base64_encode(data):
    return base64.standard_b64encode(data.encode(ENCODING)).decode(ENCODING)


def base64_decode(encoded):
    return base64.standard_b64decode(encoded)
