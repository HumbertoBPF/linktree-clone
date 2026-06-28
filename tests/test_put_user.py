import uuid

import pytest
from starlette import status

from model.serialization.model import User
from tests.utils import get_user_sid


def test_put_user_unauthorized(client):
    response = client.put("/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_successful_put_user(client, session, faker, test_user):
    put_user_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
    }

    response = client.put("/user", json=put_user_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}",
    })

    assert response.status_code == status.HTTP_200_OK

    put_user_response_body = response.json()

    assert put_user_response_body["id"] == test_user["id"]
    assert put_user_response_body["first_name"] == put_user_payload["first_name"]
    assert put_user_response_body["last_name"] == put_user_payload["last_name"]
    assert put_user_response_body["email"] == put_user_payload["email"]

    # Assert that the updated succeeded on a database level
    updated_user = session.get(User, uuid.UUID(test_user["id"]))

    assert updated_user.first_name == put_user_payload["first_name"]
    assert updated_user.last_name == put_user_payload["last_name"]
    assert updated_user.email == put_user_payload["email"]


def test_successful_put_user_same_email(client, session, faker, test_user):
    put_user_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": test_user["email"],
    }

    response = client.put("/user", json=put_user_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}",
    })

    assert response.status_code == status.HTTP_200_OK

    put_user_response_body = response.json()

    assert put_user_response_body["id"] == test_user["id"]
    assert put_user_response_body["first_name"] == put_user_payload["first_name"]
    assert put_user_response_body["last_name"] == put_user_payload["last_name"]
    assert put_user_response_body["email"] == put_user_payload["email"]

    # Assert that the updated succeeded on a database level
    updated_user = session.get(User, uuid.UUID(test_user["id"]))

    assert updated_user.first_name == put_user_payload["first_name"]
    assert updated_user.last_name == put_user_payload["last_name"]
    assert updated_user.email == put_user_payload["email"]


def test_successful_put_user_no_changes(client, session, test_user):
    response = client.put("/user", json=test_user, headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}",
    })

    assert response.status_code == status.HTTP_200_OK

    put_user_response_body = response.json()

    assert put_user_response_body["id"] == test_user["id"]
    assert put_user_response_body["first_name"] == test_user["first_name"]
    assert put_user_response_body["last_name"] == test_user["last_name"]
    assert put_user_response_body["email"] == test_user["email"]

    # Assert that the updated succeeded on a database level
    updated_user = session.get(User, uuid.UUID(test_user["id"]))

    assert updated_user.first_name == test_user["first_name"]
    assert updated_user.last_name == test_user["last_name"]
    assert updated_user.email == test_user["email"]


def test_put_user_with_existing_email(client, session, faker):
    signup_payload_user_1 = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload_user_1)

    assert response.status_code == status.HTTP_201_CREATED
    user_1_id = response.json()["id"]

    signup_payload_user_2 = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "john.doe.2@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload_user_2)

    assert response.status_code == status.HTTP_201_CREATED

    put_user_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": signup_payload_user_2["email"],
    }

    response = client.put("/user", json=put_user_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, signup_payload_user_1["email"], signup_payload_user_1["password"])}",
    })

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "user email must be unique"
    }

    # Assert that the updated failed on a database level
    user_after_update = session.get(User, uuid.UUID(user_1_id))

    assert user_after_update.first_name == signup_payload_user_1["first_name"]
    assert user_after_update.last_name == signup_payload_user_1["last_name"]
    assert user_after_update.email == signup_payload_user_1["email"]


@pytest.mark.parametrize("put_user_payload", [
    # No first name
    {
        "last_name": "Doe",
        "email": "john.doe.2@test.com"
    },
    # No last name
    {
        "first_name": "John",
        "email": "john.doe.2@test.com"
    },
    # No email
    {
        "first_name": "John",
        "last_name": "Doe",
    },
    # Invalid email
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe.2"
    },
])
def test_put_user_unprocessable_content(client, session, put_user_payload):
    signup_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED
    user_id = response.json()["id"]

    response = client.put("/user", json=put_user_payload, headers={
        "Authorization": f"Bearer {get_user_sid(client, signup_payload["email"], signup_payload["password"])}",
    })

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Assert that the updated failed on a database level
    user_after_update = session.get(User, uuid.UUID(user_id))

    assert user_after_update.first_name == signup_payload["first_name"]
    assert user_after_update.last_name == signup_payload["last_name"]
    assert user_after_update.email == signup_payload["email"]
