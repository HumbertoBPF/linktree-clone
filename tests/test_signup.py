import pytest
from starlette import status


def test_signup(client, faker):
    signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()

    assert "id" in response_body
    assert response_body["first_name"] == signup_payload["first_name"]
    assert response_body["last_name"] == signup_payload["last_name"]
    assert response_body["email"] == signup_payload["email"]
    assert "password" not in response_body


def test_signup_with_id(client, faker):
    signup_payload = {
        "id": faker.uuid4(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()

    assert response_body["id"] == signup_payload["id"]
    assert response_body["first_name"] == signup_payload["first_name"]
    assert response_body["last_name"] == signup_payload["last_name"]
    assert response_body["email"] == signup_payload["email"]
    assert "password" not in response_body


def test_signup_with_existing_id(client, faker):
    existing_user_signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "joe.doe@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=existing_user_signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response_body = response.json()

    signup_payload = {
        "id": response_body["id"],
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "joe.doe.2@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "user id must be unique"
    }


def test_signup_with_existing_email(client, faker):
    existing_user_signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=existing_user_signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": existing_user_signup_payload["email"],
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "user email must be unique"
    }


@pytest.mark.parametrize("signup_payload", [
    ({
        # Missing first name
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }),
    ({
        # Missing last name
        "first_name": "John",
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }),
    ({
        # Missing email
        "first_name": "John",
        "last_name": "Doe",
        "password": "Str0ngP@ss",
    }),
    ({
        # Missing password
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        # Invalid email
        "email": "john.doe",
        "password": "Str0ngP@ss",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        # No lowercase letter
        "password": "STR0NGP@SS",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        # No uppercase letter
        "password": "str0ngp@ss",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        # No digit
        "password": "StrOngP@ss",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        # No special character
        "password": "Str0ngP4ss",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        # Too short password
        "password": "P@sw0rd",
    }),
    ({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        # Too long password
        "password": "P@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rd",
    }),
])
def test_signup_with_unprocessable_content(client, signup_payload):
    response = client.post("/signup", json=signup_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
