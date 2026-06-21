from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BeforeValidator
from sqlmodel import SQLModel, Field, Relationship

from validation.validation import validate_email


class AuthSession(SQLModel, table=True):
    """
    Full authentication session model to be used in the database schema.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime
    expires_at: datetime
    # A link must always be owned by a user
    user_id: UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="sessions")


class LinkBase(SQLModel):
    """
    Fields that are always present in the representations of a link across the application. This simpler
    class will be used to serialize the user input at update time since ID fields are not updatable.
    """
    name: str
    url: str
    description: str | None = None


class Link(LinkBase, table=True):
    """
    Full link model to be used in the database schema.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # A link must always be owned by a user
    user_id: UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="links")


class UserBase(SQLModel):
    """
    Fields that are always present in the representations of a user across the application. This simpler
    class will be used to serialize the user input at update time since ID fields are not updatable. The password
    will not be updatable for now as well.
    """
    first_name: str
    last_name: str
    email: Annotated[str, BeforeValidator(validate_email)] = Field(index=True, unique=True)


class User(UserBase, table=True):
    """
    Full user model to be used in the database schema.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str
    links: list[Link] = Relationship(back_populates="user", cascade_delete=True)
    sessions: list[AuthSession] = Relationship(back_populates="user", cascade_delete=True)


class PublicUser(UserBase):
    """
    User representation to be returned from our APIs. The password must not be returned since it is strict
    input only information.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class SignupUser(UserBase):
    """
    User representation expected as input at signup time. Users are expected to provide:

    - first name
    - last name
    - email address
    - password

    The user ID can be provided as well. If it is not specified, it is randomly generated.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str
