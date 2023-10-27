"""Functions repository for UserData
"""
from sqlalchemy.orm import joinedload

from commissar.core.data import get_session, UserData


def save(u: UserData) -> None:
    with get_session() as session:
        session.add(u)
        session.commit()
        session.refresh(u)


def find(discord_server_id: int, discord_user_id: int) -> UserData:
    with get_session() as session:
        return session.query(UserData).options(joinedload(UserData.characters)).filter(
            UserData.discord_server_id == discord_server_id,
            UserData.discord_user_id == discord_user_id,
        ).first()


def find_by_server_id(discord_server_id: int) -> list[UserData]:
    with get_session() as session:
        return session.query(UserData).options(joinedload(UserData.characters)).filter(
            UserData.discord_server_id == discord_server_id).all()


def find_all() -> list[UserData]:
    with get_session() as session:
        return session.query(UserData).all()

