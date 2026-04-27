from fastapi import FastAPI, Response, status

from model.inmem_storage.storage import InMemLinkStorage, InMemUserStorage
from model.serialization.model import Link, SignupUser

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


@app.get("/user")
def get_user():
    return {}


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
def put_user():
    return {}


@app.delete("/user")
def delete_user():
    return {}
