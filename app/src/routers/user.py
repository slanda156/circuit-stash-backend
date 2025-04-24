from logging import getLogger
from typing import Annotated
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

import src.database as db
from src.dependencies import secrets, JWTALGORITHM, JWTEXPIRATION, FAILEDAUTHENTICATION, getCurrentUser, pwdContex
from src.schemes import Token, TokenData, User


logger = getLogger(__name__)
router = APIRouter()


def verifyPassword(hashedPassword: str, plainPassword: str, salt: str) -> bool:
    return pwdContex.verify(plainPassword + salt, hashedPassword)


def authenticateUser(username: str, password: str) -> User:
    """
    Authenticate a user by username and password.
    """
    result = db.getUser(username)
    if result is None:
        raise FAILEDAUTHENTICATION
    user, salt = result
    if user.password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to authenticate user",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not verifyPassword(user.password, password, salt):
        raise FAILEDAUTHENTICATION
    return user


def createToken(user: User, expiration: timedelta | None = None) -> Token:
    """
    Create a JWT token for the user.
    """
    if expiration is None:
        expiration = JWTEXPIRATION
    expires = datetime.now() + expiration
    if user.type is None or user.disabled is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to authenticate user",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if user.disabled:
        raise FAILEDAUTHENTICATION
    payload = TokenData(
        username=user.username,
        type=user.type,
        expiration=expires.timestamp()
    )
    token = jwt.encode(payload.model_dump(), secrets["jwt"], algorithm=JWTALGORITHM)
    return Token(access_token=token)


@router.post("/login")
def login(formData: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticateUser(formData.username, formData.password)
    token = createToken(user)
    return token


@router.get("me", response_model=User)
def getMe(currentUser: Annotated[User, Depends(getCurrentUser)]) -> User:
    return currentUser
