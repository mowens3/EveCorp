
"""Functions repository for Character
"""

from commissar.core.data import get_session, Character


def save(c: Character) -> None:
    with get_session() as session:
        session.add(c)
        session.commit()
        session.refresh(c)


def find(_id: int) -> Character:
    with get_session() as session:
        return session.query(Character).filter(Character.id == _id).first()


def find_by_character_id(character_id: int) -> Character:
    with get_session() as session:
        return session.query(Character).filter(Character.character_id == character_id).first()


def find_all() -> list[Character]:
    with get_session() as session:
        return session.query(Character).all()


def find_by_name(discord_server_id: int, character_name: str) -> list[Character]:
    with get_session() as session:
        exp = '%{}%'.format(character_name)
        res = (session.query(Character).filter(Character.discord_server_id == discord_server_id)
               .filter(Character.character_name.like(exp)))
        return res


def find_by_discord_server_id(discord_server_id: int) -> list[Character]:
    with get_session() as session:
        return session.query(Character).filter(Character.discord_server_id == discord_server_id)


def find_by_user_data_id(user_data_id: int) -> list[Character]:
    with get_session() as session:
        return session.query(Character).filter(Character.user_data_id == user_data_id)


def save_multiple(characters: list[Character]) -> None:
    with get_session() as session:
        session.bulk_save_objects(characters)
        session.commit()


def remove(c: Character) -> None:
    with get_session() as session:
        session.delete(c)
        session.commit()

