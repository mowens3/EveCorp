from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.orm import sessionmaker

from commissar.core.config import ConfigLoader

cl = ConfigLoader()
url = cl.config['postgresql']['url']
engine = create_engine(url, echo=True, future=True)


class Base(DeclarativeBase):
    pass


OAUTH_STATE_LEN = 36           # OAuth 2.0 specs. In EVE Online - GUID(32), but can be up to 2048 in OAuth 2.0 specs.
OATH_CODE_VERIFIER_LEN = 128   # OAuth 2.0 spec
DISCORD_SERVER_NAME_LEN = 200  # Discord limit
DISCORD_USER_NAME_LEN = 100    # Discord limit
DISCORD_ROLE_NAME_LEN = 50     #
CORP_NAME_LEN = 50             # EVE Online limit
CORP_TICKER_LEN = 5            # EVE Online limit
CHAR_NAME_LEN = 37             # EVE Online limit

AUTH_ATTEMPT_TTL_MINUTES = 15


class ServerSettings(Base):
    """Database entity to hold bot server specific data
    """

    # columns
    discord_server_id = Column(BigInteger(), primary_key=True)
    discord_server_name = Column(String(DISCORD_SERVER_NAME_LEN))
    discord_role_id = Column(BigInteger())
    discord_role_name = Column(String(DISCORD_ROLE_NAME_LEN))
    corporation_id = Column(BigInteger())
    corporation_name = Column(String(CORP_NAME_LEN))
    corporation_ticker = Column(String(CORP_TICKER_LEN))
    created = Column(DateTime(), default=datetime.now)
    updated = Column(DateTime(), default=None, onupdate=datetime.now)
    # meta data
    __tablename__ = 'server_settings'

    def __repr__(self):
        return "ServerSettings(id='{}' name='{}')".format(self.discord_server_id, self.discord_server_name)


class AuthAttempt(Base):
    """Database entity to hold authorization attempt data
    """

    # columns
    state = Column(String(OAUTH_STATE_LEN), primary_key=True)
    discord_server_id = Column(BigInteger(), ForeignKey('server_settings.discord_server_id'), nullable=False)
    discord_user_id = Column(BigInteger(), nullable=False)
    discord_user_name = Column(String(DISCORD_USER_NAME_LEN), nullable=False)
    discord_interaction_id = Column(BigInteger(), nullable=False)
    code_verifier = Column(String(OATH_CODE_VERIFIER_LEN), nullable=False)
    created = Column(DateTime(), default=datetime.now)
    # meta data
    __tablename__ = 'auth'

    def __repr__(self):
        return "AuthAttempt(state='{}' created='{}')".format(self.state, self.created)


class UserData(Base):
    """Database entity to hold bot user data
    """

    # columns
    id = Column(Integer(), primary_key=True)
    discord_server_id = Column(BigInteger(), ForeignKey('server_settings.discord_server_id'), nullable=False)
    discord_user_id = Column(BigInteger(), nullable=False)
    discord_user_name = Column(String(DISCORD_USER_NAME_LEN))
    created = Column(DateTime(), default=datetime.now)
    updated = Column(DateTime(), default=None, onupdate=datetime.now)
    # relations
    discord_server = relationship("ServerSettings")
    characters = relationship("Character", back_populates="user_data")
    # meta data
    __tablename__ = 'user_data'
    __table_args__ = (
        UniqueConstraint('discord_server_id', 'discord_user_id', name='server_user_unq'),
    )

    def __repr__(self):
        return "UserData(id='{}' name='{}')".format(self.discord_user_id, self.discord_user_name)


class Character(Base):
    """Database entity to hold list of bot user linked characters
    """

    # columns
    id = Column(BigInteger(), primary_key=True)
    name = Column(String(CHAR_NAME_LEN), nullable=False)
    discord_server_id = Column(BigInteger(), ForeignKey('server_settings.discord_server_id'), nullable=False)
    user_data_id = Column(BigInteger(), ForeignKey('user_data.id'), nullable=False)
    # relations
    user_data = relationship("UserData", back_populates="characters")
    discord_server = relationship("ServerSettings")
    # meta data
    __tablename__ = 'characters'


def get_session():
    generator = sessionmaker(bind=engine)
    session = generator()
    return session


# initialize database tables
Base.metadata.create_all(engine)
