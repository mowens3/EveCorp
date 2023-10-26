"""AccessInfo related functions
"""

from datetime import timedelta, datetime

from commissar_core import LOGGER
from commissar_core.oauth import AccessInfo, TokenStatus


def parse_token_response(data: dict) -> AccessInfo:
    """

    :param data: json from ESI
    :return:
    """

    expires = datetime.now() + timedelta(seconds=data['expires_in'])
    access_info = AccessInfo(data['access_token'], data['refresh_token'], expires)
    return access_info


def check_access_info(access_info) -> TokenStatus:
    """

    :param access_info:
    :return:
    """
    if access_info is not None:
        remaining = access_info.expires_at - datetime.now()
        if remaining.total_seconds() > 0:
            minutes = int(remaining.total_seconds() / 60)
            LOGGER.debug("Access Token expires in {} minutes".format(minutes))
            return TokenStatus.OK
        else:
            return TokenStatus.EXPIRED
    return TokenStatus.NA

