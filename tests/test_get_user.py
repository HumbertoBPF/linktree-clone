from starlette import status

from tests.utils import get_user_sid


def test_get_user_unauthorized(client):
    response = client.get("/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_successful_get_user(client, test_user):
    response = client.get("/user", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_200_OK

    get_user_response_body = response.json()

    assert get_user_response_body["id"] == test_user["id"]
    assert get_user_response_body["first_name"] == test_user["first_name"]
    assert get_user_response_body["last_name"] == test_user["last_name"]
    assert get_user_response_body["email"] == test_user["email"]
