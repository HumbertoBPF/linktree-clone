from starlette import status

from tests.utils import get_user_sid


def test_delete_user_unauthorized(client):
    response = client.delete("/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_delete_user_successful(client, test_user):
    response = client.delete("/user", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT
