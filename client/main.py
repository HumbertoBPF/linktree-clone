import requests


BASE_URL = "http://127.0.0.1:8000"
LINK_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a096"

USER_1_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a096"
FIRST_NAME_USER_1 = "John"
LAST_NAME_USER_1 = "Doe"
EMAIL_USER_1 = "john.doe@test.com"
PASSWORD_USER_1 = "Str0ngP@ss"

# User 2 will be updated
USER_2_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a095"
FIRST_NAME_USER_2 = "John"
LAST_NAME_USER_2 = "Doe"
EMAIL_USER_2 = "john.doe+2@test.com"
PASSWORD_USER_2 = "Str0ngP@ss"

# User 3 will be deleted
USER_3_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a094"
FIRST_NAME_USER_3 = "John"
LAST_NAME_USER_3 = "Doe"
EMAIL_USER_3 = "john.doe+3@test.com"
PASSWORD_USER_3 = "Str0ngP@ss"

# User 4 will be deleted
FIRST_NAME_USER_4 = "John"
LAST_NAME_USER_4 = "Doe"
EMAIL_USER_4 = "john.doe+4@test.com"
PASSWORD_USER_4 = "Str0ngP@ss"


def get_user_1_sid():
    payload = {
        "username": EMAIL_USER_1,
        "password": PASSWORD_USER_1
    }
    response = requests.post(f"{BASE_URL}/login", data=payload)

    assert response.status_code == 200

    return response.json()["sid"]


def get_user_2_sid():
    """This will no longer work after the user 2 is updated (the email will no longer be the same)"""
    payload = {
        "username": EMAIL_USER_2,
        "password": PASSWORD_USER_2
    }
    response = requests.post(f"{BASE_URL}/login", data=payload)

    assert response.status_code == 200

    return response.json()["sid"]


def get_user_3_sid():
    """This will no longer work after the user 3 is deleted"""
    payload = {
        "username": EMAIL_USER_3,
        "password": PASSWORD_USER_3
    }
    response = requests.post(f"{BASE_URL}/login", data=payload)

    assert response.status_code == 200

    return response.json()["sid"]


def get_links():
    response = requests.get(f"{BASE_URL}/links", headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 200


def create_link():
    # Successful request with ID
    payload = {
        "id": LINK_ID,
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # The response contains the owner user ID
    payload["user_id"] = USER_1_ID

    assert response.status_code == 201
    assert response.json() == payload

    # Successful request without ID
    payload = {
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # The response contains the owner user ID
    payload["user_id"] = USER_1_ID

    assert response.status_code == 201
    assert response.json()["id"]
    assert response.json()["name"] == payload["name"]
    assert response.json()["url"] == payload["url"]
    assert response.json()["description"] == payload["description"]
    assert response.json()["user_id"] == payload["user_id"]

    # Invalid link id (not a UUID)
    payload = {
        "id": "0c22b3d2-c321-465a-8656-a95d7fd6a06",
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Missing name (required field)
    payload = {
        "id": LINK_ID,
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Duplicate link ID (it must be unique)
    payload = {
        "id": LINK_ID,
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 409
    assert response.json() == {
        "error": "link id must be unique"
    }


def put_link():
    # Successful update
    payload = {
        "id": LINK_ID,
        "name": "Medium (updated)",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }

    response = requests.put(f"{BASE_URL}/link/{LINK_ID}", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code, "response body =", response.json())

    # The response contains the owner user ID
    payload["user_id"] = USER_1_ID

    assert response.status_code == 200
    assert response.json() == payload

    # Not found link
    payload = {
        "id": LINK_ID,
        "name": "Medium (updated)",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials"
    }

    response = requests.put(f"{BASE_URL}/link/foo", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 404
    assert response.json() == {
        "error": "Link not found"
    }


def delete_link():
    response = requests.delete(f"{BASE_URL}/link/{LINK_ID}", headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)

    assert response.status_code == 204

    response = requests.delete(f"{BASE_URL}/link/{LINK_ID}", headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 404
    assert response.json() == {
        "error": "Link not found"
    }


def create_user():
    # First successful request with ID
    payload = {
        "id": USER_1_ID,
        "first_name": FIRST_NAME_USER_1,
        "last_name": LAST_NAME_USER_1,
        "email": EMAIL_USER_1,
        "password": PASSWORD_USER_1,
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # Second successful request with ID
    payload = {
        "id": USER_2_ID,
        "first_name": FIRST_NAME_USER_2,
        "last_name": LAST_NAME_USER_2,
        "email": EMAIL_USER_2,
        "password": PASSWORD_USER_2,
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # Drop password for validation purposes since it must not be returned in the response
    payload_without_password = payload
    del payload_without_password["password"]

    assert response.status_code == 201
    assert response.json() == payload

    # Third successful request with ID
    payload = {
        "id": USER_3_ID,
        "first_name": FIRST_NAME_USER_3,
        "last_name": LAST_NAME_USER_3,
        "email": EMAIL_USER_3,
        "password": PASSWORD_USER_3,
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # Drop password for validation purposes since it must not be returned in the response
    payload_without_password = payload
    del payload_without_password["password"]

    assert response.status_code == 201
    assert response.json() == payload

    # Successful request without ID
    payload = {
        "first_name": FIRST_NAME_USER_4,
        "last_name": LAST_NAME_USER_4,
        "email": EMAIL_USER_4,
        "password": PASSWORD_USER_4,
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    response_body = response.json()

    # Drop password for validation purposes since it must not be returned in the response
    payload_without_password = payload
    del payload_without_password["password"]

    # Drop ID for validation purposes since it was not provided in the request
    del response_body["id"]

    assert response.status_code == 201
    assert response_body == payload

    # Request with duplicated user ID
    payload = {
        "id": USER_1_ID,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "Str0ngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 409
    assert response.json() == {
        "error": "user id must be unique"
    }

    # Request with duplicated user email
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": EMAIL_USER_1,
        "password": "Str0ngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 409
    assert response.json() == {
        "error": "user email must be unique"
    }

    # User without first name
    payload = {
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "Str0ngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # User without last name
    payload = {
        "first_name": "John",
        "email": "john.doe+3@test.com",
        "password": "Str0ngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # User without email
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "password": "Str0ngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # User without password
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid email
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe",
        "password": "Str0ngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid password (no lowercase)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "STR0NGP@SS",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid password (no uppercase)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "str0ngp@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid password (no digit)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "StrOngP@ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid password (no special character)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "Str0ngP4ss",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid password (too short)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "P@sw0rd",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid password (too long)
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+3@test.com",
        "password": "P@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rdP@ssw0rd",
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422


def get_user():
    # User is found
    headers = {
        "Authorization": f"Bearer {get_user_1_sid()}"
    }

    response = requests.get(f"{BASE_URL}/user", headers=headers)
    print("Status code =", response.status_code, "response body =", response.json())

    returned_user = response.json()

    assert response.status_code == 200
    assert "password" not in returned_user
    assert returned_user["id"] == USER_1_ID
    assert returned_user["first_name"] == "John"
    assert returned_user["last_name"] == "Doe"
    assert returned_user["email"] == "john.doe@test.com"

    # No authorization header
    response = requests.get(f"{BASE_URL}/user")
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 401


def put_user():
    # Successful request
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
        "email": "john.doe+200@test.com",
    }
    response = requests.put(f"{BASE_URL}/user", json=payload, headers={
        "Authorization": f"Bearer {get_user_2_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # The ID is returned in the response body
    payload["id"] = USER_2_ID

    assert response.status_code == 200
    assert response.json() == payload

    # No op update
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
    }
    response = requests.put(f"{BASE_URL}/user", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # The ID is returned in the response body
    payload["id"] = USER_1_ID

    assert response.status_code == 200
    assert response.json() == payload

    # Payload without first name
    payload = {
        "last_name": "Doe 2",
        "email": "john.doe+4@test.com",
    }
    response = requests.put(f"{BASE_URL}/user", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Payload without last name
    payload = {
        "first_name": "John 2",
        "email": "john.doe+4@test.com",
    }
    response = requests.put(f"{BASE_URL}/user", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Payload without email
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
    }
    response = requests.put(f"{BASE_URL}/user", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid email address
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
        "email": "john.doe+4",
    }
    response = requests.put(f"{BASE_URL}/user", json=payload, headers={
        "Authorization": f"Bearer {get_user_1_sid()}"
    })
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422


def delete_user():
    # User not authenticated
    response = requests.delete(f"{BASE_URL}/user")
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 401

    # User is found
    response = requests.delete(f"{BASE_URL}/user", headers={
        "Authorization": f"Bearer {get_user_3_sid()}"
    })
    print("Status code =", response.status_code)

    assert response.status_code == 204


if __name__ == "__main__":
    # Restart the server before calling this function

    # User APIs
    create_user()
    get_user()
    put_user()
    delete_user()

    # Link APIs
    get_links()
    create_link()
    put_link()
    delete_link()
