"""Functions repository for Server
"""
from commissar.core.data import get_session, Server


def create(discord_server_id: int, discord_server_name: str):
    with get_session() as session:
        server = Server(
            discord_server_id=discord_server_id,
            discord_server_name=discord_server_name
        )
        session.add(server)
        session.commit()
        return server


def find_or_create(discord_server_id: int, discord_server_name: str) -> Server:
    server = find(discord_server_id)
    if server is None:
        create(discord_server_id, discord_server_name)
    return server


def save(r: Server) -> None:
    with get_session() as session:
        session.merge(r)
        session.commit()


def find_all() -> list[Server]:
    with get_session() as session:
        return session.query(Server).all()


def find(discord_server_id: int) -> Server:
    with get_session() as session:
        return session.query(Server).filter(Server.discord_server_id == discord_server_id).first()


def remove(server: Server) -> None:
    with get_session() as session:
        session.delete(server)
        session.commit()

