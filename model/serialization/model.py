import uuid

from pydantic import BaseModel


class Link(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    name: str
    url: str
    description: str | None = None
    user_id: uuid.UUID
