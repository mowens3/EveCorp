"""Functions repository for Server
"""
from commissar.core.data import get_session, Server


def save(r: Server) -> None:
    with get_session() as session:
        session.merge(r)
        session.commit()


def find_all() -> list[Server]:
    with get_session() as session:
        return session.query(Server).all()


def find_by_discord_server_id(discord_server_id: int) -> Server:
    with get_session() as session:
        return session.query(Server).filter(Server.discord_server_id == discord_server_id).first()


def remove(server: Server) -> None:
    with get_session() as session:
        session.delete(server)
        session.commit()

