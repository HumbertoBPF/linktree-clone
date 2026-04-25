from model.serialization.model import Link


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
