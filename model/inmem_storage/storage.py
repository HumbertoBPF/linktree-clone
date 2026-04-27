from pwdlib import PasswordHash

from model.serialization.model import Link, User, SignupUser


class InMemUserStorage:
    def __init__(self):
        self.users: list[dict] = []
        self.password_hash = PasswordHash.recommended()

    def __verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def __get_password_hash(self, password):
        return self.password_hash.hash(password)

    def validate_user_uniqueness_constraints(self, user: User):
        """
        Validates that there is no users in the list with an ID or email value matching the provided user instance
        :param user: target user instance
        :return: raises a ValueError exception when there is an entry in the users list with a field violating the
        uniqueness constraints
        """
        for db_user in self.users:
            # Validate user ID uniqueness
            if str(db_user["id"]) == str(user.id):
                raise ValueError("user id must be unique")

            # Validate user email uniqueness
            if db_user["email"] == user.email:
                raise ValueError("user email must be unique")

    def insert(self, user: SignupUser):
        user_dict = user.model_dump()
        # Hash password before inserting into the database
        user_dict["password"] = self.__get_password_hash(user_dict["password"])
        self.users.append(user_dict)


class InMemLinkStorage:
    def __init__(self):
        self.links: list[dict] = []

    def validate_link_id_uniqueness(self, link_id: str):
        """
        Validates that there is no links in the list with an ID value matching the provided link_id
        :param link_id: target link_id to validate
        :return: raises a ValueError exception when there is an entry in the links list with a matching ID
        """
        for link in self.links:
            if str(link["id"]) == link_id:
                raise ValueError("link id must be unique")

    def insert(self, link: Link):
        self.links.append(link.model_dump())

    def update(self, link: Link, link_id: str) -> bool:
        """
        Update the link in the list matching the provided ID.
        :param link: new representation of the link.
        :param link_id: ID of the link to be updated.
        :return: if an item with a matching ID was found in the list.
        """
        n = len(self.links)

        for i in range(n):
            if str(self.links[i].get("id")) == link_id:
                link_dict = link.model_dump()
                # The ID must not be modified post-creation since it is typically a read-only field
                link_dict["id"] = self.links[i].get("id")
                self.links[i] = link_dict
                return True

        return False

    def delete(self, link_id: str) -> bool:
        """
        Deletes the item with the matching ID from the list.
        :param link_id: target link ID
        :return: a boolean indicating if an item with the target ID was found
        """
        n = len(self.links)

        for i in range(n):
            if str(self.links[i].get("id")) == link_id:
                del self.links[i]
                return True

        return False
