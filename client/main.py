import requests


BASE_URL = "http://127.0.0.1:8000"
LINK_ID = "0c22b3d2-c321-465a-8656-a95d7fd6a096"


def get_links():
    response = requests.get(f"{BASE_URL}/links")
    print("Status code =", response.status_code, "response body =", response.json())


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


if __name__ == "__main__":
    # Restart the server before calling this function
    get_links()
    create_link()
    put_link()
    delete_link()
