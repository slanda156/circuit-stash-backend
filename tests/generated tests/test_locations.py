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

def test_location_lifecycle(auth_headers):
    location_name = "Test Location"
    update_name = "Updated Location"

    # Create location
    response = httpx.post(
        f"{BASE_URL}/locations/",
        headers=auth_headers,
        json={"name": location_name}
    )
    assert response.status_code == 200

    # Get all locations
    response = httpx.get(f"{BASE_URL}/locations", headers=auth_headers)
    assert response.status_code == 200

    # Optional: find created location and update
    locations = response.json()
    found = None
    for locId, loc in locations.items():
        if loc["name"] == location_name:
            found = loc
            found["id"] = locId
            break
    found = next((loc for loc in locations.values() if loc["name"] == location_name), None)
    if found:
        loc_id = found["id"]
        response = httpx.put(
            f"{BASE_URL}/locations/",
            headers=auth_headers,
            json={"id": loc_id, "name": update_name}
        )
        assert response.status_code == 200

        # Get by name
        response = httpx.get(f"{BASE_URL}/locations/{update_name}", headers=auth_headers)
        assert response.status_code == 200