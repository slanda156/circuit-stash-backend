import uuid
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

from src.schemes import User, Part, Location


logger = getLogger(__name__)
VERSION = "0.1.0"
JWTALGORITHM = "HS256"
JWTEXPIRATION = timedelta(minutes=30)
FAILEDAUTHENTICATION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Username or password is incorrect",
    headers={"WWW-Authenticate": "Bearer"}
)
OAUTH2SCHEME = OAuth2PasswordBearer(tokenUrl="/user/login")
PWDCONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALLOWEDCHARS = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
    "!@#$%^()_+-=[]{}',.~°` ",
    "&*;?/\\<>\"|:",
    "\n\t\r"
]


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
    return PWDCONTEXT.hash(password + salt)


def getCurrentUser(token: Annotated[str, Depends(OAUTH2SCHEME)]) -> User:
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
        logger.debug(f"User is not admin: \"{user.username}\"")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not an admin",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def validateString(string: str) -> str:
    if string is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="String is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if type(string) is not str:
        logger.debug(f"Invalid type: \"{type(string)}\"")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="String must be string",
            headers={"WWW-Authenticate": "Bearer"}
        )
    for char in string:
        if char not in "".join(ALLOWEDCHARS):
            logger.debug(f"Invalid character in string: \"{string}\", char: \"{char}\"")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="String contains invalid characters",
                headers={"WWW-Authenticate": "Bearer"}
            )
    return string


def validatePath(path: str) -> str:
    if path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if type(path) is not str:
        logger.debug(f"Invalid type: \"{type(path)}\"")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path must be string",
            headers={"WWW-Authenticate": "Bearer"}
        )
    for char in path:
        if char not in "".join(ALLOWEDCHARS[:-2]):
            logger.debug(f"Invalid character in path: \"{path}\", char: \"{char}\"")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Path contains invalid characters",
                headers={"WWW-Authenticate": "Bearer"}
            )
    return path


def validateUUID(id: str | uuid.UUID) -> uuid.UUID:
    if id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UUID is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if type(id) not in [str, uuid.UUID]:
        logger.debug(f"Invalid type: \"{type(id)}\"")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UUID must be string",
            headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        uuid.UUID(id, version=4)
    except ValueError:
        logger.debug(f"Invalid UUID: \"{id}\"")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UUID is invalid",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return id


def validatePart(part: Part) -> Part:
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Part is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    validateString(part.name)
    if part.description is not None:
        validateString(part.description)
    if part.minStock is not None:
        if type(part.minStock) is not int:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Part minStock must be int",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if part.minStock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Part minStock must be positive",
                headers={"WWW-Authenticate": "Bearer"}
            )
    if part.image is not None:
        validatePath(part.image)
    if part.datasheet is not None:
        validatePath(part.datasheet)
    return part


def validateLocation(location: Location) -> Location:
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    validateString(location.name)
    if location.description is not None:
        validateString(location.description)
    if location.image is not None:
        validatePath(location.image)
    if location.parent is not None:
        validateUUID(location.parent)
    return location


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
