import uuid

from starlette import status

from model.serialization.model import User, Link, AuthSession
from tests.utils import get_user_sid


def test_delete_user_unauthorized(client):
    response = client.delete("/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_delete_user_successful(client, session, test_user):
    user_sid = get_user_sid(client, test_user["email"], test_user["password"])

    response = client.delete("/user", headers={
        "Authorization": f"Bearer {user_sid}"
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Assert that the deletion succeeded on the database level

    # The user must not exist anymore
    user_after_deletion = session.get(User, uuid.UUID(test_user["id"]))
    assert user_after_deletion is None

    # The auth session must not exist anymore
    auth_session_after_deletion = session.get(AuthSession, uuid.UUID(user_sid))
    assert auth_session_after_deletion is None


def test_delete_user_with_links(client, session, faker, test_user):
    link_1 = Link(
        id=uuid.UUID(faker.uuid4()),
        name="First link name",
        url=faker.url(),
        description="Text explaining what the first link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    link_2 = Link(
        id=uuid.UUID(faker.uuid4()),
        name="Second link name",
        url=faker.url(),
        description="Text explaining what the second link is",
        user_id=uuid.UUID(test_user["id"]),
    )

    session.add(link_1)
    session.add(link_2)
    session.commit()
    session.refresh(link_1)

    user_sid = get_user_sid(client, test_user["email"], test_user["password"])

    response = client.delete("/user", headers={
        "Authorization": f"Bearer {user_sid}"
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Assert that the deletion succeeded on the database level

    # The user must not exist anymore
    user_after_deletion = session.get(User, uuid.UUID(test_user["id"]))
    assert user_after_deletion is None

    # The auth session must have been cascade deleted
    auth_session_after_deletion = session.get(AuthSession, uuid.UUID(user_sid))
    assert auth_session_after_deletion is None

    # The first link must have been cascade deleted
    link_1_after_deletion = session.get(Link, link_1.id)
    assert link_1_after_deletion is None

    # The second link must have been cascade deleted
    link_2_after_deletion = session.get(Link, link_2.id)
    assert link_2_after_deletion is None
