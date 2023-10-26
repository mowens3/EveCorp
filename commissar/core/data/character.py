
"""Functions repository for Character
"""

from commissar.core.data import get_session, Character


def create(character_id: int, character_name: str, discord_server_id: int, user_data_id: int) -> None:
    session = get_session()
    c = Character(
        id=character_id,
        name=character_name,
        discord_server_id=discord_server_id,
        user_data_id=user_data_id
    )
    session.add(c)
    session.commit()


def save(c: Character) -> None:
    session = get_session()
    session.add(c)
    session.commit()
    session.refresh(c)


def find(_id: int) -> Character:
    session = get_session()
    res = session.query(Character).filter(Character.id == _id).first()
    return res


def find_by_name(discord_server_id: int, character_name: str) -> list[Character]:
    session = get_session()
    exp = '%{}%'.format(character_name)
    res = (session.query(Character).filter(Character.discord_server_id == discord_server_id)
           .filter(Character.name.like(exp)))
    return res


def find_by_user_data_id(user_data_id: int) -> list[Character]:
    session = get_session()
    res = session.query(Character).filter(Character.user_data_id == user_data_id)
    return res


def remove(_id: int) -> None:
    session = get_session()
    stmt = session.delete(Character).where(Character.id == _id)
    session.execute(stmt)
    session.commit()
