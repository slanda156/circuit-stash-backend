from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from hashlib import pbkdf2_hmac
import rsa
from base64 import b64encode, b64decode
from jose import jwt
from typing import Annotated

from src import database as db
from src.config import secrets


logger = getLogger(__name__)
router = APIRouter()


def getUser(username: str) -> db.Users | None:
    with Session(db.engine) as session:
        stmt = select(db.Users).where(db.Users.username == username)
        result = session.exec(stmt)
        user = result.first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return user


def checkUser(user: db.Users) -> bool:
    if user.type == 0:
        return True
    return False


def checkPassword(password: bytes, user: db.Users) -> bool:
    try:
        planePassword = rsa.decrypt(b64decode(password), secrets.get("privateKey", ""))
        hashedPassword = b64encode(pbkdf2_hmac("sha256", planePassword, b64decode(user.salt), 100000))

    except rsa.DecryptionError:
        logger.warning("Couldn't decrypt password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if hashedPassword == user.password:
        return True
    return False


def generateToken(user: db.Users, usableTime: int = 30) -> str:
    usableTime += 60
    data = {
        "sub": user.id,
        "exp": usableTime,
        "type": user.type
    }
    encoded_jwt = jwt.encode(data, secrets.get("jwt", ""))
    return encoded_jwt


@router.post("/login")
async def login(formData: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user = getUser(formData.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not checkUser(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not checkPassword(formData.password.encode(), user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = generateToken(user)
    return {"access_token": token, "token_type": "bearer"}
