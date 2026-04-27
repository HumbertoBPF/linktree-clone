from fastapi import FastAPI, Response, status

from model.inmem_storage.storage import InMemLinkStorage, InMemUserStorage
from model.serialization.model import Link, SignupUser, User

app = FastAPI()

link_storage = InMemLinkStorage()
user_storage = InMemUserStorage()


@app.get("/links")
def get_links():
    return {"links": link_storage.links}


@app.post("/link", status_code=status.HTTP_201_CREATED)
def create_link(link: Link, response: Response):
    try:
        link_storage.validate_link_id_uniqueness(str(link.id))
    except ValueError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "error": str(e)
        }

    # Format to dict and insert it to the in-memory storage
    link_dict = link.model_dump()
    link_storage.insert(link)
    return link_dict


@app.put("/link/{link_id}")
def update_link(link: Link, link_id: str, response: Response):
    link_dict = link.model_dump()
    if link_storage.update(link, link_id):
        return link_dict

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "Link not found"
    }


@app.delete("/link/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: str, response: Response):
    if link_storage.delete(link_id):
        return None

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "Link not found"
    }


@app.get("/user/{user_id}")
def get_user(user_id: str, response: Response):
    user = user_storage.lookup_by_id(user_id)

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


@app.put("/user/{user_id}")
def put_user(user_id: str, user: User, response: Response):
    existing_user = user_storage.lookup_by_id(user_id)

    if existing_user is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "error": "User not found"
        }

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
        updated_user["id"] = user_id
        return updated_user

    if user_storage.update(user, user_id):
        updated_user = user.model_dump()
        updated_user["id"] = user_id
        return updated_user

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "User not found"
    }


@app.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, response: Response):
    if user_storage.delete(user_id):
        return None

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "User not found"
    }
