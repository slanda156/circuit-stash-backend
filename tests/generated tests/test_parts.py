import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def token():
    response = httpx.post(
        f"{BASE_URL}/user/login",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def test_part_lifecycle(auth_headers):
    # Try to delete the part if it exists to avoid conflicts
    part_name = "TestPartFull"
    # Attempt to find the part by name
    response = httpx.get(f"{BASE_URL}/parts/", headers=auth_headers)
    if response.status_code == 200:
        parts = response.json()
        existingPart = None
        for partId, part in parts.items():
            if part.get("name") == part_name:
                existingPart = part
                existingPart["id"] = partId
                break
        if existingPart is not None:
            part_id = existingPart["id"]
            httpx.delete(f"{BASE_URL}/parts/{part_id}", headers=auth_headers)

    payload = {
        "name": part_name,
        "description": "Test Part Desc",
        "minStock": 5,
        "tags": ["a", "b"]
    }
    response = httpx.post(f"{BASE_URL}/parts/", json=payload, headers=auth_headers)
    assert response.status_code == 200

def test_get_parts(auth_headers):

    response = httpx.get(f"{BASE_URL}/parts/", headers=auth_headers)
    assert response.status_code == 200