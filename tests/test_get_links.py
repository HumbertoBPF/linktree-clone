from uuid import UUID

from starlette import status

from model.serialization.model import Link
from tests.utils import get_user_sid


def test_links_unauthorized(client):
    response = client.get("/links")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_user_with_no_links(client, test_user):
    response = client.get("/links", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "links": []
    }


def test_user_with_links(client, session, faker, test_user):
    links_1 = Link(
        name="url 1",
        url=faker.url(),
        description="description 1",
        user_id=UUID(test_user["id"]),
    )

    links_2 = Link(
        name="url 2",
        url=faker.url(),
        description="description 2",
        user_id=UUID(test_user["id"]),
    )

    session.add(links_1)
    session.add(links_2)
    session.commit()
    session.refresh(links_1)
    session.refresh(links_2)

    response = client.get("/links", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_200_OK

    response_links = response.json()["links"]

    response_link_1 = response_links[0]
    response_link_2 = response_links[1]

    assert response_link_1["id"] == str(links_1.id)
    assert response_link_1["name"] == links_1.name
    assert response_link_1["url"] == links_1.url
    assert response_link_1["description"] == links_1.description
    assert response_link_1["user_id"] == str(links_1.user_id)

    assert response_link_2["id"] == str(links_2.id)
    assert response_link_2["name"] == links_2.name
    assert response_link_2["url"] == links_2.url
    assert response_link_2["description"] == links_2.description
    assert response_link_2["user_id"] == str(links_2.user_id)
