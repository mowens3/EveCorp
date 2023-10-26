"""Functions repository for ServerSettings
"""
from core.data import get_session, ServerSettings
from core.log import LOGGER


def create(discord_server_id: int, discord_server_name: str) -> None:
    session = get_session()
    ss = ServerSettings(discord_server_id=discord_server_id, discord_server_name=discord_server_name)
    session.add(ss)
    session.commit()


def save(ss: ServerSettings) -> None:
    session = get_session()
    # insert or update
    session.merge(ss)
    session.commit()


def find_all() -> list[ServerSettings]:
    session = get_session()
    stmt = session.query(ServerSettings)
    res = stmt.all()
    return res


def find(discord_server_id) -> ServerSettings:
    session = get_session()
    res = session.query(ServerSettings).filter(ServerSettings.discord_server_id == discord_server_id).first()
    if res is None:
        LOGGER.info("Server settings with discord_server_id={} not found.".format(discord_server_id))
    return res


def check(settings: ServerSettings):
    return settings.discord_role_id is not None and settings.corporation_id is not None


def update_corporation(
        discord_server_id: int,
        corporation_id: int,
        corporation_name: str = None,
        corporation_ticker: str = None) -> None:
    session = get_session()
    res = session.query(ServerSettings).filter(ServerSettings.discord_server_id == discord_server_id)
    res.update(
        {
            ServerSettings.corporation_id: corporation_id,
            ServerSettings.corporation_name: corporation_name,
            ServerSettings.corporation_ticker: corporation_ticker
        }
    )
    session.commit()


def update_role(
        discord_server_id: int,
        discord_role_id: int,
        discord_role_name: str = None) -> None:
    session = get_session()
    res = session.query(ServerSettings).filter(ServerSettings.discord_server_id == discord_server_id)
    res.update(
        {
            ServerSettings.discord_role_id: discord_role_id,
            ServerSettings.discord_role_name: discord_role_name
        }
    )
    session.commit()

