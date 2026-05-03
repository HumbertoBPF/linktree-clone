from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from model.inmem_storage.storage import InMemLinkStorage, InMemUserStorage, InMemSessionStorage
from model.serialization.model import Link, SignupUser, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

link_storage = InMemLinkStorage()
user_storage = InMemUserStorage()
session_storage = InMemSessionStorage()


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    session = session_storage.lookup_by_id(token)
    if not session or (session["expires_at"] <= datetime.now()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_storage.lookup_by_id(str(session["user_id"]))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def authenticate_user(username: str, password: str) -> dict | None:
    user = user_storage.lookup_by_email(username)
    if not user:
        return None

    if user_storage.verify_password(password, user["password"]):
        return user

    return None


@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = session_storage.insert(user["id"])
    return {
        "sid": session_id
    }


@app.get("/links")
def get_links(user: Annotated[dict, Depends(get_current_user)]):
    return {"links": link_storage.lookup_by_user_id(user_id=str(user["id"]))}


@app.post("/link", status_code=status.HTTP_201_CREATED)
def create_link(user: Annotated[dict, Depends(get_current_user)], link: Link, response: Response):
    try:
        link_storage.validate_link_id_uniqueness(str(link.id))
    except ValueError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "error": str(e)
        }

    # Format to dict and insert it to the in-memory storage
    link_dict = link.model_dump()
    link_storage.insert(link=link, user_id=str(user["id"]))
    link_dict["user_id"] = str(user["id"])
    return link_dict


@app.put("/link/{link_id}")
def update_link(user: Annotated[dict, Depends(get_current_user)], link: Link, link_id: str, response: Response):
    link_dict = link.model_dump()
    if link_storage.update(link=link, link_id=link_id, user_id=str(user["id"])):
        link_dict["user_id"] = str(user["id"])
        return link_dict

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "Link not found"
    }


@app.delete("/link/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(user: Annotated[dict, Depends(get_current_user)], link_id: str, response: Response):
    if link_storage.delete(link_id=link_id, user_id=str(user["id"])):
        return None

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "Link not found"
    }


@app.get("/user")
def get_user(user: Annotated[dict, Depends(get_current_user)], response: Response):
    if user is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "error": "User not found"
        }

    # Remove the password from the returned user since this is sensible information
    del user["password"]
    return user


@app.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user(user: SignupUser, response: Response):
    try:
        user_storage.validate_user_uniqueness_constraints(user)
    except ValueError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "error": str(e)
        }

    user_storage.insert(user)
    user_without_password = user.model_dump()
    del user_without_password["password"]
    return user_without_password


@app.put("/user")
def put_user(existing_user: Annotated[dict, Depends(get_current_user)], user: User, response: Response):
    # No need to validate email uniqueness if the email is kept the same
    if existing_user["email"] != user.email:
        try:
            user_storage.validate_email_uniqueness_constraint(user)
        except ValueError as e:
            response.status_code = status.HTTP_409_CONFLICT
            return {
                "error": str(e)
            }

    # No-op if the users have the same fields
    if (
        (existing_user["first_name"] == user.first_name) and
        (existing_user["last_name"] == user.last_name) and
        (existing_user["email"] == user.email)
    ):
        updated_user = user.model_dump()
        updated_user["id"] = existing_user["id"]
        return updated_user

    if user_storage.update(user, str(existing_user["id"])):
        updated_user = user.model_dump()
        updated_user["id"] = existing_user["id"]
        return updated_user

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "User not found"
    }


@app.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user: Annotated[dict, Depends(get_current_user)], response: Response):
    if user_storage.delete(str(user["id"])):
        return None

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "User not found"
    }
