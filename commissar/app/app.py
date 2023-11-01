"""Flask app for handling OAuth 2.0 callbacks and some other basic stuff
"""
from flask import Flask, request, render_template
from httpx import HTTPError

from commissar import ConfigLoader
from commissar.core.data import Character, UserData, character_repo
from commissar.core.data import auth_attempt_repo, user_data_repo
from commissar.core.esi.esi import ESI
from commissar import LOGGER
from commissar.core.oauth.helpers import validate
from commissar.core.oauth.oauth_service import OAuthService
from commissar.app import APP_NAME, AppException

cfg = ConfigLoader().config
host = cfg['app']['hostname']
port = cfg['app']['port']
app = Flask(APP_NAME)


@app.route('/')
@app.route('/index.html')
def index():
    LOGGER.debug(request.path)
    return render_template("index.html", title=APP_NAME)


@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    status_code = 200
    result_code = None
    result_text = None
    message = None
    try:
        if code is None:
            raise AppException(400, 100, "Request doesn't contain 'code' argument")
        if state is None:
            raise AppException(400, 101, "Request doesn't contain 'state' argument")
        attempt = auth_attempt_repo.find(state)
        if attempt is None:
            raise AppException(404, 103, "Pending Authorization data not found or expired")
        access_info = None
        try:
            access_info = OAuthService().get_access_token(code, attempt.code_verifier)
        except HTTPError as e:
            LOGGER.error(e)
        if access_info is not None:
            character_id, character_name = validate(access_info.access_token)
            u = user_data_repo.find(attempt.discord_server_id, attempt.discord_user_id)
            if u is None:
                LOGGER.info("User not yet registered.")
                u = UserData(
                    discord_server_id=attempt.discord_server_id,
                    discord_user_id=attempt.discord_user_id,
                    discord_user_name=attempt.discord_user_name
                )
                user_data_repo.save(u)
            else:
                LOGGER.info("Character has been registered already.")
                character_ids = [c.id for c in u.characters]
                if character_id in character_ids:
                    raise AppException(304, 104, "Character has been registered already.")
            data = ESI().get_character(character_id)
            corporation_id = data['corporation_id']
            alliance_id = data['alliance_id'] if 'alliance_id' in data else None
            c = Character(
                discord_server_id=attempt.discord_server_id,
                user_data_id=u.id,
                character_id=character_id,
                character_name=character_name,
                corporation_id=corporation_id,
                alliance_id=alliance_id
            )
            character_repo.save(c)
            LOGGER.info("Character registered successfully.")
            status_code = 201
            result_code = 0
            result_text = 'REGISTERED'
            message = 'Character registered successfully. You can close this page and return to Discord server.'
    except AppException as e:
        LOGGER.error(e)
        status_code = e.http_status_code
        result_code = e.error_code
        result_text = "FAIL"
        message = e.__str__()
    except Exception as e:
        LOGGER.error(e, exc_info=True)
        status_code = 503
        result_code = -1
        result_text = "FAIL"
        message = "Something went wrong."
    finally:
        return render_template(
            "result.html",
            title=APP_NAME,
            result_code=result_code,
            result_text=result_text,
            message=message
        ), status_code


def start():
    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=False
    )

