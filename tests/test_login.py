import pytest
from starlette import status


def test_login_random_credentials(client, test_user):
    response = client.post("/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
    })

    assert response.status_code == status.HTTP_200_OK
    assert "sid" in response.json()


def test_login_known_credentials(client, faker):
    signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/login", data={
        "username": signup_payload["email"],
        "password": signup_payload["password"]
    })

    assert response.status_code == status.HTTP_200_OK
    assert "sid" in response.json()


@pytest.mark.parametrize("login_payload", [
    ({
        "username": "john.doe.2@test.com",
        "password": "Str0ngP@ss"
    }),
    ({
        "username": "john.doe@test.com",
        "password": "invalid-Str0ngP@ss"
    }),
])
def test_login_with_wrong_credentials(client, faker, login_payload):
    signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/login", data=login_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


@pytest.mark.parametrize("login_payload", [
    ({"username": "john.doe@test.com"}),
    ({"password": "Str0ngP@ss"}),
    ({}),
])
def test_login_with_missing_credential(client, faker, login_payload):
    signup_payload = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
    }

    response = client.post("/signup", json=signup_payload)

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/login", data=login_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
