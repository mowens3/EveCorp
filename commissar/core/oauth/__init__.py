import enum
import json
from datetime import datetime


class TokenStatus(enum.Enum):
    """
    Enum for different states of OAuth 2.0 Access Tokens
    """
    NA = 0
    EXPIRED = 1
    OK = 2


class AuthorizationInfo:
    """ OAuth 2.0 meta data
    """

    def __init__(self, code_verifier: str, state: str, location_url: str):
        self.code_verifier = code_verifier
        self.state = state
        self.location_url = location_url


class AccessInfo:
    """Class for storing Access Token Info
    """

    def __init__(self, access_token: str, refresh_token: str, expires_at: datetime = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at




class CharacterInfo:
    """Class for storing Character Data
    """
    DTF = "%Y-%m-%d %H:%M:%S"

    def __init__(self,
                 character_id: int,
                 character_name: str,
                 discord_user_id: int,
                 access_info: AccessInfo = None):
        self.character_id = character_id
        self.character_name = character_name
        self.discord_user_id = character_name
        self.access_info = access_info

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)