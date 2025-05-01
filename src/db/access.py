import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import INTEGER, TEXT, TIMESTAMP

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
