from fastapi import FastAPI, Response, status

from model.inmem_storage.storage import InMemStorage
from model.serialization.model import Link
from validation.validation import validate_link_id_uniqueness

app = FastAPI()

storage = InMemStorage()


@app.get("/links")
def get_links():
    return {"links": storage.links}


@app.post("/link", status_code=status.HTTP_201_CREATED)
def create_link(link: Link, response: Response):
    try:
        validate_link_id_uniqueness(storage.links, str(link.id))
    except ValueError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "error": str(e)
        }

    # Format to dict and insert it to the in-memory storage
    link_dict = link.model_dump()
    storage.insert(link)
    return link_dict


@app.put("/link/{link_id}")
def update_link(link: Link, link_id: str, response: Response):
    link_dict = link.model_dump()
    if storage.update(link, link_id):
        return link_dict

    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "Link not found"
    }


@app.delete("/link/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: str, response: Response):
    if storage.delete(link_id):
        return None
    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "error": "Link not found"
    }
