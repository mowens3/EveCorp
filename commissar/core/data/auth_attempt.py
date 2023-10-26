from datetime import datetime, timedelta

from commissar.core.data import get_session, AuthAttempt, AUTH_ATTEMPT_TTL_MINUTES


def save(a: AuthAttempt) -> None:
    session = get_session()
    session.add(a)
    session.commit()
    session.refresh(a)


def find(state: str) -> AuthAttempt:
    session = get_session()
    res = session.query(AuthAttempt).filter(AuthAttempt.state == state).first()
    return res


def remove(state: str) -> None:
    session = get_session()
    stmt = session.delete(AuthAttempt).where(AuthAttempt.state == state)
    session.execute(stmt)
    session.commit()


def remove_expired() -> int:
    session = get_session()
    limit = datetime.now() - timedelta(minutes=AUTH_ATTEMPT_TTL_MINUTES)
    result = session.query(AuthAttempt).where(AuthAttempt.created <= limit).delete()
    session.commit()
    return result


def find_expired() -> list[AuthAttempt]:
    session = get_session()
    limit = datetime.now() - timedelta(minutes=AUTH_ATTEMPT_TTL_MINUTES)
    stmt = session.query(AuthAttempt).filter(AuthAttempt.created <= limit)
    res = stmt.all()
    return res
