import os
from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4, UUID

from dotenv import load_dotenv
from fastapi import Depends
from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from exceptions.exceptions import UniquenessError
from model.serialization.model import Link, User, SignupUser, UserBase, LinkBase, AuthSession

SESSION_EXPIRATION_MINUTES = 60

# Injects the .env file values into os.environ
load_dotenv()

# Access them normally
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_IP_ADDRESS = os.getenv("MYSQL_IP_ADDRESS")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE_NAME = os.getenv("MYSQL_DATABASE_NAME")

mysql_url = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_IP_ADDRESS}:{MYSQL_PORT}/{MYSQL_DATABASE_NAME}"

engine = create_engine(mysql_url)


def get_db_session():
    with Session(engine) as db_session:
        yield db_session


# For dependency injection in the application layer
DbSessionDep = Annotated[Session, Depends(get_db_session)]


class InMemSessionStorage:
    def __validate_session_id_uniqueness_constraint(self, db_session: DbSessionDep, session_id: UUID):
        """
        Validates that there is no sessions in the list with an ID value matching the provided session_id
        :param db_session: database session object
        :param session_id: session ID under validation
        :return: raises a UniquenessError exception when there is an entry in the session list with a field violating the
        uniqueness constraints
        """
        if self.lookup_by_id(db_session, session_id):
            raise UniquenessError("user id must be unique")

    def lookup_by_id(self, db_session: DbSessionDep, session_id: UUID):
        """
        Queries the session with the provided ID
        :param db_session: database session object
        :param session_id: target session ID
        :return: the session record matching the provided ID. It returns None if no such object exists
        """
        auth_session = db_session.get(AuthSession, session_id)
        if auth_session:
            return auth_session

        return None

    def insert(self, db_session: DbSessionDep, user_id: UUID) -> UUID:
        """
        Creates and inserts a session object associated with the provided user ID
        :param db_session: database session object
        :param user_id: ID of the user owning the session and, therefore, authenticated in the app
        :return: the ID of the created session (to be used to authenticate the user)
        """
        session_id = uuid4()

        self.__validate_session_id_uniqueness_constraint(db_session, session_id)

        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=SESSION_EXPIRATION_MINUTES)
        auth_session = AuthSession(id=session_id, user_id=user_id, created_at=created_at, expires_at=expires_at)
        db_session.add(auth_session)
        db_session.commit()

        return session_id


class InMemUserStorage:
    def __init__(self):
        self.password_hash = PasswordHash.recommended()

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def __get_password_hash(self, password):
        return self.password_hash.hash(password)

    def validate_user_uniqueness_constraints(self, db_session: DbSessionDep, user: SignupUser):
        """
        Validates that there is no users in the list with an ID or email value matching the provided user instance
        :param db_session: database session object
        :param user: target user instance
        :return: raises a UniquenessError exception when there is an entry in the users list with a field violating the
        uniqueness constraints
        """
        if self.lookup_by_id(db_session, user.id):
            raise UniquenessError("user id must be unique")

        try:
            self.lookup_by_email(db_session, user.email)
        except NoResultFound:
            return

        raise UniquenessError("user email must be unique")

    def lookup_by_email(self, db_session: DbSessionDep, email: str) -> User | None:
        """
        Searches for a user with the provided email.
        :param db_session: database session object
        :param email: target email
        :return: returns the user with a matching email or None if there is no such a user
        """
        stmt = select(User).where(User.email == email)
        results = db_session.exec(stmt)

        if results:
            # Because of the uniqueness constraint, we know that only a single record is returned, if any is returned
            return results.one()

        return None

    def lookup_by_id(self, db_session: DbSessionDep, user_id: UUID):
        """
        Searches for a user with the provided ID.
        :param db_session: database session object
        :param user_id: target user ID
        :return: returns the user with a matching ID or None if there is no such a user
        """
        user = db_session.get(User, user_id)

        if user:
            return user

        return None

    def insert(self, db_session: DbSessionDep, user: SignupUser):
        """
        Creates a user in the database with the provided signup data.
        :param db_session: database session object
        :param user: signup data
        :return: the created user
        """
        # Hash password before inserting into the database
        user.password = self.__get_password_hash(user.password)
        # Validate the user model
        user_db = User.model_validate(user)
        # Insert the user into the database
        db_session.add(user_db)
        db_session.commit()
        db_session.refresh(user_db)
        return user_db

    def update(self, db_session: DbSessionDep, user: UserBase, existing_user: User) -> User:
        """
        Patches the data of an existing user with the input data
        :param db_session: database session object
        :param user: new representation of the user (excluding the password).
        :param existing_user: user to be updated.
        :return: the updated user.
        """
        user_data = user.model_dump()
        existing_user.sqlmodel_update(user_data)
        db_session.add(existing_user)
        db_session.commit()
        db_session.refresh(existing_user)
        return existing_user

    def delete(self, db_session: DbSessionDep, user: User):
        """
        Deletes the specified user from the database.
        :param db_session: database session object
        :param user: user to be deleted
        """
        db_session.delete(user)
        db_session.commit()


class InMemLinkStorage:
    def validate_link_id_uniqueness(self, db_session: DbSessionDep, link_id: UUID):
        """
        Validates that there is no links in the list with an ID value matching the provided link_id
        :param db_session: database session object
        :param link_id: target link_id to validate
        :return: raises a UniquenessError exception when there is an entry in the links list with a matching ID
        """
        if self.lookup_by_id(db_session, link_id):
            raise UniquenessError("link id must be unique")

    def lookup_by_id(self, db_session: DbSessionDep, link_id: UUID):
        """
        Queries the database for a link with the provided ID
        :param db_session: database session object
        :param link_id: target link ID
        :return: the link entity with the provided ID. Returns None if there is no such entity
        """
        link = db_session.get(Link, link_id)

        if link:
            return link

        return None

    def lookup_by_user_id(self, db_session: DbSessionDep, user_id: UUID):
        """
        Queries the database for all link owned by the user with the provided IDs
        :param db_session: database session object
        :param user_id: target user ID
        :return: the link entities owned by the provided user. Returns None if there is no such entity
        """
        stmt = select(Link).join(User).where(User.id == user_id)
        results = db_session.exec(stmt)
        return results.all()

    def insert(self, db_session: DbSessionDep, link: Link, user: User):
        """
        Creates a link with the provided data into the database.
        :param db_session: database session object
        :param link: link to be inserted
        :param user: user that is authenticated
        :return: the user that was inserted into the database
        """
        # Validate the link model
        link_db = Link.model_validate(link, update={
            "user": user,
            "user_id": user.id,
        })
        db_session.add(link_db)
        # Insert the link into the database
        db_session.commit()
        db_session.refresh(link_db)
        return link_db

    def update(self, db_session: DbSessionDep, link: LinkBase, existing_link: Link):
        """
        Update the link in the list matching the provided ID.
        :param db_session: database session object
        :param link: new representation of the link
        :param existing_link: existing link
        :return: if an item with a matching ID was found in the list.
        """
        link_data = link.model_dump()
        existing_link.sqlmodel_update(link_data)
        db_session.add(existing_link)
        db_session.commit()
        db_session.refresh(existing_link)
        return existing_link

    def delete(self, db_session: DbSessionDep, link: Link):
        """
        Deletes the specified link
        :param db_session: database session object
        :param link: link to be deleted
        """
        db_session.delete(link)
        db_session.commit()
