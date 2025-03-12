from fastapi import FastAPI, Query, Cookie, Header, Body, status, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from Enums.core_enum import ModelNameEnum
from Exceptions.unicorn_exception import UnicornException
from Models.hero_mode import Hero
from Models.item_model import ItemModel, FilterModel, UserInModel, UserOutModel, LoginInModel
from pydantic import AfterValidator
from Validators.get_item_request_validator import check_valid_id
import time
from contextlib import asynccontextmanager

from config.engine import create_db_and_tables, SessionDep

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.post("/heroes")
async def store_hero(session: SessionDep, hero: Hero) -> Hero:
    try:
        if Hero.model_validate(hero):
            session.add(hero)
            session.commit()
            session.refresh(hero)
            return hero
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Hello World"}

@app.post("/login", status_code=status.HTTP_200_OK)
def login(login_request: Annotated[LoginInModel, Form()]):
    return {**login_request.model_dump()}

@app.post("/user/files")
async def store_file(file: Annotated[bytes, File()], file_b: Annotated[UploadFile, File()]):
    return {"file": len(file), "file_b": file_b.content_type}

@app.post("/items/{item_id}", status_code=status.HTTP_201_CREATED)
def get_items(item_id: Annotated[int, AfterValidator(check_valid_id)],
              item: ItemModel,
              user: UserInModel,
              limit: Annotated[FilterModel, Query(description="Fetch limited record")]
             ):
    if item.quantity == 0:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Quantity should be more than 0", headers={"x-error": "Error"})

    if item.price == 10:
        raise UnicornException(name="Unicorn Flying")

    return [{"item_d": item_id, **limit.model_dump(), **item.model_dump(), **user.model_dump()}]

@app.get("/models/{model_name}", status_code=status.HTTP_200_OK)
def get_models(model_name: ModelNameEnum, ad_id: Annotated[str | None, Cookie()] = None, x_token: Annotated[str | None, Header()] = None):
    return {"model": model_name, "ad_id": ad_id, "x-token": x_token}

@app.get("/items", status_code=status.HTTP_200_OK)
def store_item(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"item": token}

@app.post("/user", response_model=UserOutModel, status_code=status.HTTP_201_CREATED)
def store_user(user: Annotated[UserInModel, Body()]):
    return {**user.model_dump()}


