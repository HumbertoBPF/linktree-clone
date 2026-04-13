def validate_link_id_uniqueness(links: list[dict], link_id: str):
    """
    Validates that there is no links in the list with an ID value matching the provided link_id
    :param links: in-memory list of links
    :param link_id: target link_id to validate
    :return: raises a ValueError exception when there is an entry in the links list with a matching ID
    """
    for link in links:
        if str(link["id"]) == link_id:
            raise ValueError("link id must be unique")
