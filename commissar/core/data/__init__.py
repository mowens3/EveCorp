from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, DateTime, String, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.orm import sessionmaker

from commissar import ConfigLoader

cl = ConfigLoader()
url = cl.config['postgresql']['url']
engine = create_engine(url, echo=False, echo_pool=False, future=True)
session_generator = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


OAUTH_STATE_LEN = 36            # OAuth 2.0 specs. In EVE Online - GUID(32), but can be up to 2048 in OAuth 2.0 specs.
OATH_CODE_VERIFIER_LEN = 128    # OAuth 2.0 spec
DISCORD_SERVER_NAME_LEN = 200   # Discord limit
DISCORD_USER_NAME_LEN = 100     # Discord limit
DISCORD_ROLE_NAME_LEN = 50      #
DISCORD_CHANNEL_NAME_LEN = 100  # Discord limit
CORP_NAME_LEN = 50              # EVE Online limit
CORP_TICKER_LEN = 5             # EVE Online limit
CHAR_NAME_LEN = 37              # EVE Online limit
LOCALE_LEN = 5                  # Discord limit

AUTH_ATTEMPT_TTL_MINUTES = 60


class ServerRule(Base):
    """Database entity to hold bot server specific data
    """

    id = Column(BigInteger(), primary_key=True)
    discord_server_id = Column(BigInteger(), unique=True, nullable=False)
    discord_server_name = Column(String(DISCORD_SERVER_NAME_LEN), nullable=False)
    discord_role_id = Column(BigInteger(), nullable=False)
    discord_role_name = Column(String(DISCORD_ROLE_NAME_LEN))
    corporation_id = Column(BigInteger(), nullable=False)
    corporation_name = Column(String(CORP_NAME_LEN))
    corporation_ticker = Column(String(CORP_TICKER_LEN))
    discord_channel_id = Column(BigInteger(), nullable=False)
    discord_channel_name = Column(String(DISCORD_CHANNEL_NAME_LEN))
    locale = Column(String(LOCALE_LEN), nullable=True)
    created = Column(DateTime(), default=datetime.now)
    updated = Column(DateTime(), default=None, onupdate=datetime.now)

    __tablename__ = 'server_rule'
    __table_args__ = (
        UniqueConstraint('discord_server_id', 'discord_role_id', name='server_rule_unq'),
    )

    def __repr__(self):
        return "DiscordServerRule(id='{}')".format(self.id)


class AuthAttempt(Base):
    """Database entity to hold authorization attempt data
    """

    state = Column(String(OAUTH_STATE_LEN), primary_key=True)
    discord_server_id = Column(BigInteger(), nullable=False)
    discord_user_id = Column(BigInteger(), nullable=False)
    discord_user_name = Column(String(DISCORD_USER_NAME_LEN), nullable=False)
    code_verifier = Column(String(OATH_CODE_VERIFIER_LEN), nullable=False)
    created = Column(DateTime(), default=datetime.now)
    expire = Column(DateTime(), default=datetime.now() + timedelta(minutes=AUTH_ATTEMPT_TTL_MINUTES))

    __tablename__ = 'auth'

    def __repr__(self):
        return "AuthAttempt(state='{}' created='{}')".format(self.state, self.created)


class UserData(Base):
    """Database entity to hold bot user data
    """

    id = Column(Integer(), primary_key=True)
    discord_server_id = Column(BigInteger(), nullable=False)
    discord_user_id = Column(BigInteger(), nullable=False)
    discord_user_name = Column(String(DISCORD_USER_NAME_LEN))
    created = Column(DateTime(), default=datetime.now)
    updated = Column(DateTime(), default=None, onupdate=datetime.now)

    characters = relationship("Character", back_populates="user_data")

    __tablename__ = 'user_data'
    __table_args__ = (
        UniqueConstraint('discord_server_id', 'discord_user_id', name='server_user_unq'),
    )

    def __repr__(self):
        return "UserData(id='{}' name='{}')".format(self.discord_user_id, self.discord_user_name)


class Character(Base):
    """Database entity to hold list of bot user linked characters
    """

    id = Column(BigInteger(), primary_key=True)
    discord_server_id = Column(BigInteger(), nullable=False)
    user_data_id = Column(BigInteger(), ForeignKey('user_data.id'), nullable=False)
    character_id = Column(BigInteger(), nullable=False)
    character_name = Column(String(CHAR_NAME_LEN), nullable=False)
    corporation_id = Column(BigInteger(), nullable=True)
    alliance_id = Column(BigInteger(), nullable=True)
    created = Column(DateTime(), default=datetime.now)
    updated = Column(DateTime(), default=None, onupdate=datetime.now)

    user_data = relationship("UserData", back_populates="characters")

    __tablename__ = 'characters'
    __table_args__ = (
        UniqueConstraint('discord_server_id', 'character_id', name='character_unq'),
    )

    def __repr__(self):
        return "Character(id='{}' name='{}')".format(self.character_id, self.character_name)


@contextmanager
def get_session():
    session = session_generator()
    try:
        yield session
    finally:
        session.close()


# initialize database tables
Base.metadata.create_all(engine)
