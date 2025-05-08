import datetime
import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import INTEGER, TEXT, TIMESTAMP, VARCHAR


class Token(BaseModel):
    access_token: str
    token_type: str


load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")
ALG = "HS256"

dialect = "mysql"
username = "root"
password = "password"
host = "db"
port = "3306"
database = "db_memo"
engine = create_engine(f"{dialect}://{username}:{password}@{host}:{port}/{database}")
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

    if title is not None:
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

    password_hash = pwd_context.hash(password)
    user = User(username=user, password=password_hash)
    session.add(user)
    session.commit()
    return user


def create_access_token(
    data: dict[str, str], expires_delta: timedelta = timedelta(minutes=15)
):
    to_encode = data.copy()
    expire = datetime.datetime.now() + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALG)
    print(encoded_jwt)
    return encoded_jwt


def login_user(user: str, password: str) -> str | None:
    row = session.query(User.password).filter(User.username == user).first()
    if row is None:
        return None
    hashed = row.tuple()[0]
    if pwd_context.verify(password, hashed):
        return create_access_token({"sub": user})
    else:
        return None


def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALG])
        username = payload.get("sub")
        if username is None:
            return False
    except Exception:
        return False
    return _exists_user(username)
