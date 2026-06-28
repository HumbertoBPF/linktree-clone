import uuid

import pytest
from starlette import status

from model.serialization.model import Link
from tests.utils import get_user_sid


def test_create_link_unauthorized(client):
    response = client.post("/link")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_create_link_successful(client, session, faker, test_user):
    create_link_payload = {
        "name": "Link name",
        "url": faker.url(),
        "description": "Text explaining what this link is"
    }

    response = client.post("/link", json=create_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_201_CREATED

    create_link_response_body = response.json()

    assert "id" in create_link_response_body
    assert create_link_response_body["name"] == create_link_payload["name"]
    assert create_link_response_body["url"] == create_link_payload["url"]
    assert create_link_response_body["description"] == create_link_payload["description"]
    assert create_link_response_body["user_id"] == test_user["id"]

    # Assert that the user was created on the database level
    created_link = session.get(Link, uuid.UUID(create_link_response_body["id"]))

    assert created_link.name == create_link_payload["name"]
    assert created_link.url == create_link_payload["url"]
    assert created_link.description == create_link_payload["description"]
    assert str(created_link.user_id) == test_user["id"]


def test_create_link_successful_with_specific_id(client, session, faker, test_user):
    create_link_payload = {
        "id": faker.uuid4(),
        "name": "Link name",
        "url": faker.url(),
        "description": "Text explaining what this link is"
    }

    response = client.post("/link", json=create_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_201_CREATED

    create_link_response_body = response.json()

    assert create_link_response_body["id"] == create_link_payload["id"]
    assert create_link_response_body["name"] == create_link_payload["name"]
    assert create_link_response_body["url"] == create_link_payload["url"]
    assert create_link_response_body["description"] == create_link_payload["description"]
    assert create_link_response_body["user_id"] == test_user["id"]

    # Assert that the user was created on the database level
    created_link = session.get(Link, uuid.UUID(create_link_payload["id"]))

    assert str(created_link.id) == create_link_payload["id"]
    assert created_link.name == create_link_payload["name"]
    assert created_link.url == create_link_payload["url"]
    assert created_link.description == create_link_payload["description"]
    assert str(created_link.user_id) == test_user["id"]


def test_create_link_successful_without_description(client, session, faker, test_user):
    create_link_payload = {
        "name": "Link name",
        "url": faker.url(),
    }

    response = client.post("/link", json=create_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_201_CREATED

    create_link_response_body = response.json()

    assert "id" in create_link_response_body
    assert create_link_response_body["name"] == create_link_payload["name"]
    assert create_link_response_body["url"] == create_link_payload["url"]
    assert create_link_response_body["description"] is None
    assert create_link_response_body["user_id"] == test_user["id"]

    # Assert that the user was created on the database level
    created_link = session.get(Link, uuid.UUID(create_link_response_body["id"]))

    assert created_link.name == create_link_payload["name"]
    assert created_link.url == create_link_payload["url"]
    assert created_link.description is None
    assert str(created_link.user_id) == test_user["id"]


def test_create_link_successful_with_existing_id_owned_by_the_same_user(client, session, faker, test_user):
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

    create_link_payload = {
        "id": str(link.id),
        "name": "Another link name",
        "url": faker.url(),
        "description": "Text explaining what this link is"
    }

    response = client.post("/link", json=create_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "link id must be unique"
    }


def test_create_link_successful_with_existing_id_owned_by_another_user(client, session, faker, test_user):
    signup_payload_user_2 = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload_user_2)

    assert response.status_code == status.HTTP_201_CREATED

    signup_response_body_user_2 = response.json()

    link = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Link name",
        url=faker.url(),
        description="Text explaining what this link is",
        user_id=uuid.UUID(signup_response_body_user_2["id"]),
    )

    session.add(link)
    session.commit()
    session.refresh(link)

    create_link_payload = {
        "id": str(link.id),
        "name": "Another link name",
        "url": faker.url(),
        "description": "Text explaining what this link is"
    }

    response = client.post("/link", json=create_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "link id must be unique"
    }


@pytest.mark.parametrize(
    "create_link_payload", [
        # No name
        {
            "url": "www.google.com",
        },
        # No url
        {
            "name": "Link name",
        }
    ]
)
def test_create_link_unprocessable_content(client, faker, create_link_payload):
    signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/link", json=create_link_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, signup_payload["email"], signup_payload["password"])}"
    })

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
