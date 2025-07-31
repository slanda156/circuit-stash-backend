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

def test_user_me(auth_headers):
    response = httpx.get(f"{BASE_URL}/userme", headers=auth_headers)
    assert response.status_code == 200
    assert "username" in response.json()