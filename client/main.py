import requests


BASE_URL = "http://127.0.0.1:8000"
LINK_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a096"
USER_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a096"


def get_links():
    response = requests.get(f"{BASE_URL}/links")
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 200


def create_link():
    # Successful request with ID
    payload = {
        "id": LINK_ID,
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 201
    assert response.json() == payload

    # Successful request without ID
    payload = {
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

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
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid user id (not a UUID)
    payload = {
        "id": LINK_ID,
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb31c"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Missing name (required field)
    payload = {
        "id": LINK_ID,
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Duplicate link ID (it must be unique)
    payload = {
        "id": LINK_ID,
        "name": "Medium",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }
    response = requests.post(f"{BASE_URL}/link", json=payload)
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
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }

    response = requests.put(f"{BASE_URL}/link/{LINK_ID}", json=payload)
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 200
    assert response.json() == payload

    # Not found link
    payload = {
        "id": LINK_ID,
        "name": "Medium (updated)",
        "url": "https://medium.com/@humbertofilho_30158",
        "description": "My Medium blog, where I write programming-related articles and tutorials",
        "user_id": "d30964d7-d92c-4671-b016-e334fedb318c"
    }

    response = requests.put(f"{BASE_URL}/link/foo", json=payload)
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 404
    assert response.json() == {
        "error": "Link not found"
    }


def delete_link():
    response = requests.delete(f"{BASE_URL}/link/{LINK_ID}")
    print("Status code =", response.status_code)

    assert response.status_code == 204

    response = requests.delete(f"{BASE_URL}/link/{LINK_ID}")
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 404
    assert response.json() == {
        "error": "Link not found"
    }


def create_user():
    # Successful request with ID
    payload = {
        "id": USER_ID,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "password": "Str0ngP@ss",
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
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe+2@test.com",
        "password": "Str0ngP@ss",
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
        "id": USER_ID,
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
        "email": "john.doe@test.com",
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
    response = requests.get(f"{BASE_URL}/user/{USER_ID}")
    print("Status code =", response.status_code, "response body =", response.json())

    returned_user = response.json()

    assert response.status_code == 200
    assert "password" not in returned_user
    assert returned_user["id"] == USER_ID
    assert returned_user["first_name"] == "John"
    assert returned_user["last_name"] == "Doe"
    assert returned_user["email"] == "john.doe@test.com"

    # User was not found
    response = requests.get(f"{BASE_URL}/user/foo")
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 404
    assert response.json() == {
        "error": "User not found"
    }


def put_user():
    # Successful request with ID
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
        "email": "john.doe+3@test.com",
    }
    response = requests.put(f"{BASE_URL}/user/{USER_ID}", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # The ID is returned in the response body
    payload["id"] = USER_ID

    assert response.status_code == 200
    assert response.json() == payload

    # No op update
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
        "email": "john.doe+3@test.com",
    }
    response = requests.put(f"{BASE_URL}/user/{USER_ID}", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    # The ID is returned in the response body
    payload["id"] = USER_ID

    assert response.status_code == 200
    assert response.json() == payload

    # Payload without first name
    payload = {
        "last_name": "Doe 2",
        "email": "john.doe+3@test.com",
    }
    response = requests.put(f"{BASE_URL}/user/{USER_ID}", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Payload without last name
    payload = {
        "first_name": "John 2",
        "email": "john.doe+3@test.com",
    }
    response = requests.put(f"{BASE_URL}/user/{USER_ID}", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Payload without email
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
    }
    response = requests.put(f"{BASE_URL}/user/{USER_ID}", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422

    # Invalid email address
    payload = {
        "first_name": "John 2",
        "last_name": "Doe 2",
        "email": "john.doe+3",
    }
    response = requests.put(f"{BASE_URL}/user/{USER_ID}", json=payload)
    print("Status code =", response.status_code)
    print("response body =", response.json())

    assert response.status_code == 422


def delete_user():
    # User is found
    response = requests.delete(f"{BASE_URL}/user/{USER_ID}")
    print("Status code =", response.status_code)

    assert response.status_code == 204

    # User was not found
    response = requests.delete(f"{BASE_URL}/user/foo")
    print("Status code =", response.status_code, "response body =", response.json())

    assert response.status_code == 404
    assert response.json() == {
        "error": "User not found"
    }


def get_user_sid():
    payload = {
        "username": "john.doe@test.com",
        "password": "Str0ngP@ss"
    }
    response = requests.post(f"{BASE_URL}/login", data=payload)

    assert response.status_code == 200

    return response.json()["sid"]


if __name__ == "__main__":
    # Restart the server before calling this function

    # Link APIs
    get_links()
    create_link()
    put_link()
    delete_link()

    # User APIs
    create_user()
    print("sid =", get_user_sid())
    get_user()
    put_user()
    delete_user()
