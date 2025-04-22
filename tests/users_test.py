import rsa
import logging
from base64 import b64encode
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
logger = logging.getLogger("logger")

with open("secrets/public.key", "rb") as f:
    publicKey = rsa.PublicKey.load_pkcs1(f.read())


def testUserCreate():
    username = "test"
    password = b"test"

    url = "/user/login/"

    entPassword = b64encode(rsa.encrypt(password, publicKey)).decode()

    response = client.post(
        url,
        data={"username": username, "password": entPassword}
        )

    assert response.status_code == 200
