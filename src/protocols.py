import datetime

from pydantic import BaseModel


class BaseQuery(BaseModel):
    title: str
    content: str | None = None


class BaseResponse(BaseModel):
    id: int
    title: str
    content: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


InsertQuery = UpdateQuery = BaseQuery
InsertResponse = GetResponse = UpdateResponse = BaseResponse
