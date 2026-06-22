from faker import Faker
from starlette import status
from starlette.testclient import TestClient


def get_user_sid(client: TestClient, email: str, password: str) -> str:
    response = client.post("/login", data={
        "username": email,
        "password": password
    })

    assert response.status_code == status.HTTP_200_OK

    return response.json()["sid"]

