"""Functions repository for UserData
"""

from commissar.core.data import get_session, UserData


def create(discord_server_id: int, discord_user_id: int, discord_user_name: str) -> None:
    session = get_session()
    u = UserData(
        discord_server_id=discord_server_id,
        discord_user_id=discord_user_id,
        discord_user_name=discord_user_name
    )
    session.add(u)
    session.commit()


def save(u: UserData) -> None:
    session = get_session()
    session.add(u)
    session.commit()
    session.refresh(u)


def find(discord_server_id: int, discord_user_id: int) -> UserData:
    session = get_session()
    res = session.query(UserData).filter(
        UserData.discord_server_id == discord_server_id,
        UserData.discord_user_id == discord_user_id,
    ).first()
    return res


def find_all(discord_server_id: int) -> list[UserData]:
    session = get_session()
    res = session.query(UserData).filter(UserData.discord_server_id == discord_server_id)
    return res
