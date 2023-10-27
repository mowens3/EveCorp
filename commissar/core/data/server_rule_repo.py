"""Functions repository for ServerRule
"""
from commissar.core.data import get_session, ServerRule


def save(r: ServerRule) -> None:
    with get_session() as session:
        session.merge(r)
        session.commit()


def find_all() -> list[ServerRule]:
    with get_session() as session:
        return session.query(ServerRule).all()


def find_by_id(_id: int) -> ServerRule:
    with get_session() as session:
        return session.query(ServerRule).filter(ServerRule.id == _id).first()


def find_by_discord_server_id(discord_server_id: int) -> list[ServerRule]:
    with get_session() as session:
        return session.query(ServerRule).filter(ServerRule.discord_server_id == discord_server_id).all()


def find_by_server_id_and_role_id(discord_server_id: int, discord_role_id: int) -> ServerRule:
    with get_session() as session:
        return session.query(ServerRule).filter(
            ServerRule.discord_server_id == discord_server_id,
            ServerRule.discord_role_id == discord_role_id,
        ).first()


def remove(rule: ServerRule) -> None:
    with get_session() as session:
        session.delete(rule)
        session.commit()

