import uuid

import pytest
from starlette import status

from model.serialization.model import Link
from tests.utils import get_user_sid


def test_put_link_unauthorized(client, session, faker, test_user):
    link = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Link name",
        url=faker.url(),
        description="Text explaining what this link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    response = client.put(f"/link/{link.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_put_link_successful(client, session, faker, test_user):
    link = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Link name",
        url=faker.url(),
        description="Text explaining what this link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    put_link_payload = {
        "name": "New link name",
        "url": faker.url(),
        "description": "New text explaining what this link is"
    }

    response = client.put(f"/link/{link.id}", json=put_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_200_OK

    put_link_response_body = response.json()

    assert put_link_response_body["id"] == str(link.id)
    assert put_link_response_body["name"] == put_link_payload["name"]
    assert put_link_response_body["url"] == put_link_payload["url"]
    assert put_link_response_body["description"] == put_link_payload["description"]
    assert put_link_response_body["user_id"] == test_user["id"]


def test_put_link_no_description(client, session, faker, test_user):
    link = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Link name",
        url=faker.url(),
        description="Text explaining what this link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    put_link_payload = {
        "name": "New link name",
        "url": faker.url(),
    }

    response = client.put(f"/link/{link.id}", json=put_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_200_OK

    put_link_response_body = response.json()

    assert put_link_response_body["id"] == str(link.id)
    assert put_link_response_body["name"] == put_link_payload["name"]
    assert put_link_response_body["url"] == put_link_payload["url"]
    assert put_link_response_body["description"] is None
    assert put_link_response_body["user_id"] == test_user["id"]


def test_put_link_no_changes(client, session, faker, test_user):
    link = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Link name",
        url=faker.url(),
        description="Text explaining what this link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    put_link_payload = {
        "name": link.name,
        "url": link.url,
        "description": link.description
    }

    response = client.put(f"/link/{link.id}", json=put_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_200_OK

    put_link_response_body = response.json()

    assert put_link_response_body["id"] == str(link.id)
    assert put_link_response_body["name"] == link.name
    assert put_link_response_body["url"] == link.url
    assert put_link_response_body["description"] == link.description
    assert put_link_response_body["user_id"] == test_user["id"]


@pytest.mark.parametrize("put_link_payload", [
    # No name
    {
        "url": "www.google.com",
    },
    # No url
    {
        "name": "Link name",
    }
])
def test_put_link_unprocessable_content(client, session, faker, test_user, put_link_payload):
    link = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Link name",
        url=faker.url(),
        description="Text explaining what this link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    response = client.put(f"/link/{link.id}", json=put_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
