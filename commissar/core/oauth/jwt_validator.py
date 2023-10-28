import httpx
from jose import jwt, ExpiredSignatureError, JWTError

from commissar import LOGGER


class JWTValidator:
    """Class for validating Java Web Token (JWT) data from EVE Online Authorization API
    """

    SSO_META_DATA_URL = "https://login.eveonline.com/.well-known/oauth-authorization-server"
    JWK_ALGORITHM = "RS256"
    JWK_ISSUERS = ("login.eveonline.com", "https://login.eveonline.com")
    JWK_AUDIENCE = "EVE Online"

    @staticmethod
    def __validate_eve_jwt(token: str) -> dict:
        """Validate a JWT access token retrieved from the EVE SSO.
        :param token: A JWT access token originating from the EVE SSO
        :return: contents of the validated JWT access token if there are no errors
        """
        client = httpx.Client()
        try:
            # fetch JWKs URL from meta data endpoint
            res = client.get(JWTValidator.SSO_META_DATA_URL)
            res.raise_for_status()
            data = res.json()
            jwks_uri = data["jwks_uri"]
        except ConnectionError as e:
            raise RuntimeError("Couldn't contact validation service", e)
        except KeyError as e:
            raise RuntimeError(
                f"Invalid data received from the SSO meta data endpoint: {data}", e
            ) from None

        # fetch JWKs from endpoint
        res = client.get(jwks_uri)
        res.raise_for_status()
        data = res.json()
        try:
            jwk_sets = data["keys"]
        except KeyError:
            raise RuntimeError(
                f"Invalid data received from the the jwks endpoint: {data}"
            ) from None

        # pick the JWK with the requested alogorithm
        jwk_set = [item for item in jwk_sets if item["alg"] == JWTValidator.JWK_ALGORITHM].pop()

        # try to decode the token and validate it against expected values
        # will raise JWT exceptions if decoding fails or expected values do not match
        content = jwt.decode(
            token=token,
            key=jwk_set,
            algorithms=jwk_set["alg"],
            issuer=JWTValidator.JWK_ISSUERS,
            audience=JWTValidator.JWK_AUDIENCE,
        )
        return content

    @staticmethod
    def validate(token) -> tuple:
        """Validate Access Token and extract some useful values from it
        :param token: OAuth 2.0 access token
        :return: 3 values tuple
        """
        try:
            token_content = JWTValidator.__validate_eve_jwt(token)
            LOGGER.debug(token_content)
        except ExpiredSignatureError as e:
            LOGGER.warn("The JWT token has expired")
            raise e
        except JWTError as e:
            LOGGER.error(f"The JWT token was invalid: {e}")
            raise e
        except RuntimeError as e:
            LOGGER.error(str(e))
            raise e
        else:
            yield token_content['tenant']
            yield token_content['sub']
            yield token_content['name']

