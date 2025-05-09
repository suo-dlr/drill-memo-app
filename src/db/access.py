import datetime

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import INTEGER, TEXT, TIMESTAMP, VARCHAR

from auth import create_access_token, hash_password, verify_password, verify_token


class Token(BaseModel):
    access_token: str
    token_type: str


dialect = "mysql"
username = "root"
password = "password"
host = "db"
port = "3306"
database = "db_memo"
engine = create_engine(f"{dialect}://{username}:{password}@{host}:{port}/{database}")
Base = declarative_base()


class Memo(Base):
    __tablename__ = "memo"
    id = Column(INTEGER, primary_key=True)
    title = Column(TEXT, nullable=False)
    content = Column(TEXT)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    updated_at = Column(
        TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )


class User(Base):
    __tablename__ = "users"
    id = Column(INTEGER, primary_key=True)
    username = Column(VARCHAR(20), nullable=False, unique=True)
    password = Column(VARCHAR(100), nullable=False)


SessionClass = sessionmaker(engine)
session = SessionClass()


def insert_memo(title: str, content: str | None) -> Memo:
    memo = Memo(title=title, content=content)
    session.add(memo)
    session.commit()
    return memo


def select_memo_by_id(id: int) -> Memo | None:
    return session.query(Memo).filter(Memo.id == id).first()


def update_memo_by_id(id: int, title: str, content: str | None) -> Memo | None:
    memo = select_memo_by_id(id)
    if memo is None:
        return None

    memo.title = title
    if content is not None:
        memo.content = content
    session.commit()
    return memo


def delete_memo_by_id(id: int) -> bool:
    memo = select_memo_by_id(id)
    if memo is None:
        return False

    session.delete(memo)
    session.commit()
    return True


def _exists_user(user: str):
    return session.query(User).filter(User.username == user).count() >= 1


def register_user(user: str, password: str) -> User | None:
    if _exists_user(user):
        return None

    password_hash = hash_password(password)
    user = User(username=user, password=password_hash)
    session.add(user)
    session.commit()
    return user


def login_user(user: str, password: str) -> str | None:
    row = session.query(User.password).filter(User.username == user).first()
    if row is None:
        return None
    hashed = row.tuple()[0]
    if verify_password(password, hashed):
        return create_access_token({"sub": user})
    else:
        return None


def verify_user(token: str) -> bool:
    user = verify_token(token)
    if user is None:
        return False
    return _exists_user(user)
