import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from sqlmodel import SQLModel
from starlette.responses import JSONResponse

from exceptions.exceptions import UniquenessError
from model.storage.storage import InMemLinkStorage, InMemUserStorage, InMemSessionStorage, engine, DbSessionDep
from model.serialization.model import Link, SignupUser, User, PublicUser, UserBase, LinkBase
from validation.validation import validate_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

link_storage = InMemLinkStorage()
user_storage = InMemUserStorage()
session_storage = InMemSessionStorage()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db_session: DbSessionDep):
    session = session_storage.lookup_by_id(db_session, uuid.UUID(token))
    if not session or (session.expires_at <= datetime.now()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_storage.lookup_by_id(db_session, uuid.UUID(str(session.user_id)))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def authenticate_user(db_session: DbSessionDep, username: str, password: str):
    try:
        user = user_storage.lookup_by_email(db_session, username)
    except NoResultFound:
        return None

    if user_storage.verify_password(password, user.password):
        return user

    return None


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Returns validation errors with a 422 response code"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"message": exc.errors()},
    )


@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: DbSessionDep):
    user = authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = session_storage.insert(db_session, user.id)
    return {
        "sid": session_id
    }


@app.get("/health")
def health():
    return {"name": "linktree-clone"}


@app.get("/links")
def get_links(db_session: DbSessionDep, user: Annotated[User, Depends(get_current_user)]):
    return {"links": link_storage.lookup_by_user_id(db_session=db_session, user_id=user.id)}


@app.post("/link", status_code=status.HTTP_201_CREATED)
def create_link(db_session: DbSessionDep, user: Annotated[User, Depends(get_current_user)], link: Link):
    try:
        link_id = uuid.UUID(str(link.id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="The id must be an hexadecimal UUID string")

    try:
        link_storage.validate_link_id_uniqueness(db_session=db_session, link_id=link_id)
    except UniquenessError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    created_link = link_storage.insert(db_session=db_session, link=link, user=user)
    return created_link


@app.put("/link/{link_id}")
def update_link(db_session: DbSessionDep, user: Annotated[User, Depends(get_current_user)], link: LinkBase, link_id: str):
    try:
        link_uuid = uuid.UUID(str(link_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="The id must be an hexadecimal UUID string")

    existing_link = link_storage.lookup_by_id(db_session, link_uuid)

    if existing_link is None or existing_link.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    return link_storage.update(db_session=db_session, link=link, existing_link=existing_link)


@app.delete("/link/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(db_session: DbSessionDep, user: Annotated[User, Depends(get_current_user)], link_id: str):
    try:
        link_uuid = uuid.UUID(str(link_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="The id must be an hexadecimal UUID string")

    link = link_storage.lookup_by_id(db_session, link_uuid)

    if link is None or link.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    link_storage.delete(db_session=db_session, link=link)
    return None


@app.get("/user", response_model=PublicUser)
def get_user(user: Annotated[User, Depends(get_current_user)]):
    return user.model_dump()


@app.post("/signup", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
def create_user(db_session: DbSessionDep, user: SignupUser):
    try:
        validate_password(user.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    try:
        user_storage.validate_user_uniqueness_constraints(db_session, user)
    except UniquenessError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    created_user = user_storage.insert(db_session, user)
    return created_user.model_dump()


@app.put("/user", response_model=PublicUser)
def put_user(db_session: DbSessionDep, existing_user: Annotated[User, Depends(get_current_user)], user: UserBase):
    try:
        user_holding_email = user_storage.lookup_by_email(db_session, user.email)
    except NoResultFound:
        updated_user = user_storage.update(db_session, user, existing_user)
        return updated_user.model_dump()

    # If there is a user with the provided email, it must be the same user, otherwise there is a uniqueness conflict
    if (user_holding_email is not None) and (user_holding_email.id != existing_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user email must be unique")

    updated_user = user_storage.update(db_session, user, existing_user)
    return updated_user.model_dump()


@app.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db_session: DbSessionDep, user: Annotated[User, Depends(get_current_user)]):
    user_storage.delete(db_session, user)
    return None
