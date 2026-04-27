import uuid
from typing import Annotated

from pydantic import BaseModel, BeforeValidator

from validation.validation import validate_email, validate_password


class Link(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    name: str
    url: str
    description: str | None = None
    user_id: uuid.UUID


class User(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    first_name: str
    last_name: str
    email: Annotated[str, BeforeValidator(validate_email)]


class SignupUser(User):
    password: Annotated[str, BeforeValidator(validate_password)]

