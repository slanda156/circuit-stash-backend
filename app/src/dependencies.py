from logging import getLogger
from pathlib import Path
from typing import Optional, Annotated
from datetime import datetime, timedelta
from base64 import b64decode

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, Field
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.schemes import User


logger = getLogger(__name__)
VERSION = "0.1.0"
JWTALGORITHM = "HS256"
JWTEXPIRATION = timedelta(minutes=30)
FAILEDAUTHENTICATION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Username or password is incorrect",
    headers={"WWW-Authenticate": "Bearer"}
)
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
pwdContex = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Config(BaseModel):
    """
    Configuration class for the application.
    """
    # Database settings
    dbType: str = Field(default="sqlite")
    dbFile: Optional[str] = Field(default="db.db")
    dbHost: Optional[str] = Field(default=None)
    dbPort: Optional[int] = Field(default=None)
    dbUser: Optional[str] = Field(default=None)
    dbPassword: Optional[str] = Field(default=None)


def getPasswordHash(password: str, salt: str) -> str:
    return pwdContex.hash(password + salt)


def getCurrentUser(token: Annotated[str, Depends(oauth2Scheme)]) -> User:
    try:
        data = jwt.decode(token, secrets["jwt"], algorithms=[JWTALGORITHM])
        username = data.get("username")
        userType = data.get("type")
        expiration = data.get("expiration")
        if username is None or userType is None or expiration is None:
            logger.debug("Token is missing required fields")
            raise FAILEDAUTHENTICATION
        if datetime.now() > datetime.fromtimestamp(expiration):
            logger.debug("Token is expired")
            raise FAILEDAUTHENTICATION
    except InvalidTokenError:
        logger.debug("Token is invalid")
        raise FAILEDAUTHENTICATION
    user = User(
        username=username,
        type=userType,
        disabled=False
    )
    return user


def isAdmin(user: Annotated[User, Depends(getCurrentUser)]) -> User:
    if user.type != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not an admin",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


configPath = Path("data/config.json")
if not configPath.exists():
    logger.warning("Config file not found. Creating default config.")
    with open(configPath, "w") as f:
        config = Config()
        f.write(config.model_dump_json(indent=4))
        logger.info("Default config created")

with open("data/config.json", "r") as f:
    config = Config.model_validate_json(f.read())
    logger.info("Config loaded")

secrets = {}
with open("data/secrets/jwt.txt", "rb") as f:
    jwtSecret = b64decode(f.read())
secrets["jwt"] = jwtSecret

logger.info("Secrets loaded")
