from fastapi import FastAPI, HTTPException

from db import delete_memo_by_id, insert_memo, select_memo_by_id, update_memo_by_id
from protocols import (
    GetResponse,
    InsertQuery,
    InsertResponse,
    UpdateQuery,
    UpdateResponse,
)

app = FastAPI()


@app.post("/api/memos", response_model=InsertResponse, status_code=201)
async def insert(query: InsertQuery):
    memo = insert_memo(query.title, query.content)
    return InsertResponse.model_validate(memo)


@app.get("/api/memos/{id}", response_model=GetResponse, status_code=200)
async def get_memo(id: int):
    memo = select_memo_by_id(id)
    if memo is not None:
        return GetResponse.model_validate(memo)
    else:
        raise HTTPException(status_code=404)


@app.put("/api/memos/{id}", response_model=UpdateResponse, status_code=200)
async def update_memo(id: int, query: UpdateQuery):
    memo = update_memo_by_id(id, query.title, query.content)
    if memo is None:
        raise HTTPException(status_code=404)
    else:
        return UpdateResponse.model_validate(memo)


@app.delete("/api/memos/{id}", status_code=204)
async def delete_memo(id: int):
    if not delete_memo_by_id(id):
        raise HTTPException(status_code=404)
