from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, BeforeValidator, Field

from validation.validation import validate_email, validate_password


class Link(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    url: str
    description: str | None = None
    user_id: UUID


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: Annotated[str, BeforeValidator(validate_email)]


class SignupUser(User):
    password: Annotated[str, BeforeValidator(validate_password)]

