import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
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
    created_at = Column(TIMESTAMP, default=datetime.datetime.now())
    updated_at = Column(
        TIMESTAMP, default=datetime.datetime.now(), onupdate=datetime.datetime.now()
    )


class InsertQuery(BaseModel):
    title: str
    content: str | None = Field(None)


class InsertResponse(BaseModel):
    id: int
    title: str
    content: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


app = FastAPI()

SessionClass = sessionmaker(engine)
session = SessionClass()


@app.get("/")
async def index():
    return {"message": "Hello World!"}


@app.post("/api/memos", response_model=InsertResponse, status_code=201)
async def insert(query: InsertQuery):
    new_memo = Memo(title=query.title, content=query.content)
    session.add(new_memo)
    session.commit()
    return InsertResponse.model_validate(new_memo)


@app.get("/api/memos/{id}", response_model=InsertResponse, status_code=200)
async def get_memo(id: int):
    res = session.query(Memo).filter(Memo.id == id).first()
    if res is not None:
        return InsertResponse.model_validate(res)
    else:
        raise HTTPException(status_code=404)


@app.put("/api/memos/{id}", response_model=InsertResponse, status_code=200)
async def update_memo(id: int, query: InsertQuery):
    memo = session.query(Memo).filter(Memo.id == id).first()
    if memo is None:
        raise HTTPException(status_code=404)
    else:
        memo.title = query.title
        memo.content = query.content
        session.commit()
        return InsertResponse.model_validate(memo)


@app.delete("/api/memos/{id}", status_code=204)
async def delete_memo(id: int):
    memo = session.query(Memo).filter(Memo.id == id).first()
    if memo is None:
        raise HTTPException(status_code=404)
    else:
        session.delete(memo)
        session.commit()
