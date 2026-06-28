import uuid

from starlette import status

from model.serialization.model import Link
from tests.utils import get_user_sid


def test_delete_link_unauthorized(client, session, faker, test_user):
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

    response = client.delete(f"/link/{link.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_delete_link_successful(client, session, faker, test_user):
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

    response = client.delete(f"/link/{link.id}", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Assert that the deletion succeeded on the database level
    link_after_deletion = session.get(Link, link.id)
    assert link_after_deletion is None


def test_delete_link_not_found(client, faker, test_user):
    response = client.delete(f"/link/{faker.uuid4()}", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Link not found"
    }


def test_delete_link_unprocessable_content(client, test_user):
    response = client.delete(f"/link/foo", headers={
        "Authorization": f"Bearer {get_user_sid(client, test_user["email"], test_user["password"])}"
    })

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {
        "detail": "The id must be an hexadecimal UUID string"
    }
