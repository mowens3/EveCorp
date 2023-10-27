from datetime import datetime, timedelta

from commissar.core.data import get_session, AuthAttempt, AUTH_ATTEMPT_TTL_MINUTES


def save(a: AuthAttempt) -> None:
    with get_session() as session:
        session.add(a)
        session.commit()
        session.refresh(a)


def find(state: str) -> AuthAttempt:
    with get_session() as session:
        return session.query(AuthAttempt).filter(AuthAttempt.state == state).first()


def remove(state: str) -> None:
    with get_session() as session:
        stmt = session.delete(AuthAttempt).where(AuthAttempt.state == state)
        session.execute(stmt)
        session.commit()


def remove_expired() -> int:
    with get_session() as session:
        result = session.query(AuthAttempt).where(AuthAttempt.expire <= datetime.now()).delete()
        session.commit()
        return result


def find_expired() -> list[AuthAttempt]:
    with get_session() as session:
        return session.query(AuthAttempt).filter(AuthAttempt.expire <= datetime.now()).all()
