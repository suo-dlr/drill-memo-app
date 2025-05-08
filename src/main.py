import re

from fastapi import FastAPI, Header, HTTPException

from db import (
    delete_memo_by_id,
    insert_memo,
    login_user,
    register_user,
    select_memo_by_id,
    update_memo_by_id,
    verify_token,
)
from protocols import (
    GetResponse,
    InsertQuery,
    InsertResponse,
    LoginQuery,
    LoginResponse,
    RegisterQuery,
    RegisterResponse,
    UpdateQuery,
    UpdateResponse,
)

app = FastAPI()


@app.post("/api/memos", response_model=InsertResponse, status_code=201)
async def insert(query: InsertQuery, authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401)
    token = re.match("Bearer\s(\S*)", authorization)
    if token is None:
        raise HTTPException(401)
    print(token.group(1))
    if not verify_token(token.group(1)):
        raise HTTPException(401)

    memo = insert_memo(query.title, query.content)
    return InsertResponse.model_validate(memo)


@app.get("/api/memos/{id}", response_model=GetResponse, status_code=200)
async def get_memo(id: int, authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401)
    token = re.match("Bearer\s(\S*)", authorization)
    if token is None:
        raise HTTPException(401)
    print(token.group(1))
    if not verify_token(token.group(1)):
        raise HTTPException(401)

    memo = select_memo_by_id(id)
    if memo is not None:
        return GetResponse.model_validate(memo)
    else:
        raise HTTPException(status_code=404)


@app.put("/api/memos/{id}", response_model=UpdateResponse, status_code=200)
async def update_memo(
    id: int, query: UpdateQuery, authorization: str | None = Header(default=None)
):
    if authorization is None:
        raise HTTPException(401)
    token = re.match("Bearer\s(\S*)", authorization)
    if token is None:
        raise HTTPException(401)
    print(token.group(1))
    if not verify_token(token.group(1)):
        raise HTTPException(401)

    memo = update_memo_by_id(id, query.title, query.content)
    if memo is None:
        raise HTTPException(status_code=404)
    else:
        return UpdateResponse.model_validate(memo)


@app.delete("/api/memos/{id}", status_code=204)
async def delete_memo(id: int, authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401)
    token = re.match("Bearer\s(\S*)", authorization)
    if token is None:
        raise HTTPException(401)
    if not verify_token(token.group(1)):
        raise HTTPException(401)

    if not delete_memo_by_id(id):
        raise HTTPException(status_code=404)


@app.post("/api/users/register", status_code=201)
def register(query: RegisterQuery):
    user = register_user(query.username, query.password)
    if user is None:
        raise HTTPException(status_code=409)
    else:
        return RegisterResponse.model_validate(user)


@app.post("/api/users/login", response_model=LoginResponse, status_code=200)
def login(query: LoginQuery):
    token = login_user(query.username, query.password)
    if token is None:
        raise HTTPException(status_code=401)
    else:
        return LoginResponse(token=token)
