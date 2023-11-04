import json
import uuid

import httpx

from commissar import ConfigLoader
from commissar import LOGGER
from commissar import SingletonMeta
from commissar.core.oauth import AccessInfo, AuthorizationInfo, TokenStatus
from commissar.core.oauth import helpers
from commissar.core.oauth.access_info import parse_token_response, check_access_info


class OAuthService(metaclass=SingletonMeta):
    """Class for handling OAuth 2.0 interactions with EVE Online Authorization API: https://login.eveonline.com/v2/oauth
    """

    HOST = 'login.eveonline.com'
    BASE_URL = 'https://login.eveonline.com/v2/oauth'
    CONTENT_TYPE = 'application/x-www-form-urlencoded'

    def __init__(self):
        try:
            cfg = ConfigLoader().config
            self.client_id = cfg['esi']['client_id']
            self.client_secret = cfg['esi']['client_secret']
            self.auth_header = helpers.get_authorization_header_value(self.client_id, self.client_secret)
            self.scopes = cfg['esi']['scopes']
            self.callback_url = cfg['esi']['callback_url']
            self.callback_host = cfg['esi']['callback_host']
        except KeyError as e:
            LOGGER.warn(e, exc_info=True)

    def authorize(self) -> AuthorizationInfo:
        """OAuth 2.0 authorize call
        :return: authorization info
        """
        code_verifier = helpers.gen_code_verifier()
        state = str(uuid.uuid1())
        code_challenge = helpers.gen_code_challenge(code_verifier)
        params = {
            'response_type': 'code',
            'redirect_uri': self.callback_url,
            'client_id': self.client_id,
            'scope': " ".join(self.scopes),
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'state': state
        }
        url = "".join([OAuthService.BASE_URL, '/authorize/'])
        response = httpx.get(url, params=params)
        if response.status_code == 302:
            location_url = response.headers["location"]
            i = AuthorizationInfo(code_verifier, state, location_url)
            return i
        else:
            LOGGER.error(response.text)

    def get_access_token(self, code: str, code_verifier: str) -> AccessInfo:
        """OAuth 2.0 access token call
        :param code: Authorization Code from OAuth 2.0 authorize
        :param code_verifier: Code Verifier
        :return: Access Token info
        """
        headers = {
            "Content-Type": OAuthService.CONTENT_TYPE,
            "Host": OAuthService.HOST,
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "code_verifier": code_verifier
        }
        url = "".join([OAuthService.BASE_URL, '/token'])
        response = httpx.post(url, headers=headers, data=payload)
        access_info = None
        if response.status_code == 200:
            access_info = parse_token_response(response.json())
        else:
            LOGGER.error(response.text)
            _json = json.loads(response.text)
            raise RuntimeError(_json['error_description'])
        return access_info

    def refresh_access_token(self, refresh_token: str) -> AccessInfo:
        """OAuth 2.0 refresh access token call
        :param refresh_token: Refresh Token from current Access Token info
        :return: refreshed Access Token info
        """
        headers = {
            "Content-Type": OAuthService.CONTENT_TYPE,
            "Host": OAuthService.HOST,
            "Authorization": self.auth_header
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        url = "".join([OAuthService.BASE_URL, '/token'])
        response = httpx.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            return parse_token_response(response.json())
        else:
            LOGGER.error(response.text)
            _json = json.loads(response.text)
            raise RuntimeError(_json['error_description'])

    def refresh_access_token_if_needed(self, access_info: AccessInfo) -> AccessInfo:
        """Method for handling optionally expired Access Token
        :param access_info: current Access Token info
        :return: optionally updated Access Token info
        """
        status = check_access_info(access_info)
        result = None
        match status:
            case TokenStatus.OK:
                LOGGER.info("Access Token is OK.")
                result = access_info
            case TokenStatus.EXPIRED:
                LOGGER.info("Access Token has expired. Refreshing...")
                result = self.refresh_access_token(access_info.refresh_token)
            case TokenStatus.NA:
                pass
        return result

