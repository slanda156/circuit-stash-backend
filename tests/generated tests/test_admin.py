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

def test_admin_user_lifecycle(auth_headers):
    username = "apitestuser"
    password = "testpass"
    user_type = 2
    httpx.post(f"{BASE_URL}/admin/user/user", headers=auth_headers, params={"username": username, "password": password, "type": user_type})
    httpx.put(f"{BASE_URL}/admin/users/user", headers=auth_headers, json={"username": username, "disabled": False, "type": 1})
    httpx.delete(f"{BASE_URL}/admin/users/user", headers=auth_headers, params={"username": username})

def test_admin_get_users(auth_headers):
    response = httpx.get(f"{BASE_URL}/admin/users", headers=auth_headers)
    assert response.status_code == 200

def test_admin_configs(auth_headers):
    name, value = "testconfig", "12345"
    httpx.post(f"{BASE_URL}/admin/configs", headers=auth_headers, params={"name": name, "value": value})
    response = httpx.get(f"{BASE_URL}/admin/configs/{name}", headers=auth_headers)
    assert response.status_code == 200
    response = httpx.get(f"{BASE_URL}/admin/configs", headers=auth_headers)
    assert response.status_code == 200
