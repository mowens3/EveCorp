"""Functions repository for UserData
"""
from sqlalchemy.orm import joinedload

from commissar import LOGGER
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


def find_by_server_id_paginate(discord_server_id: int, page: int = 1, per_page: int = 10) -> dict:
    with get_session() as session:
        offset = (page-1) * per_page
        stmt = session.query(UserData).options(joinedload(UserData.characters)).filter(
            UserData.discord_server_id == discord_server_id)
        count = stmt.count()
        pages = count // per_page
        if count % per_page > 0:
            pages += 1
        _prev = page - 1 if page > 1 else None
        _next = page + 1 if page < pages else None
        LOGGER.info("count={} pages={} prev={} next={}".format(count, pages, _prev, _next))
        paged_results = stmt.limit(per_page).offset(offset).all()
        return {
            "count": count,
            "pages": pages,
            "users": paged_results,
            "current": page,
            "prev": _prev,
            "next": _next
        }


def find_all() -> list[UserData]:
    with get_session() as session:
        return session.query(UserData).all()

