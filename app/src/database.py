import os
from logging import getLogger
from typing import Optional
from base64 import b64encode

from fastapi import HTTPException, status
from sqlmodel import SQLModel, Field, create_engine
from sqlmodel import Session, select

from src.dependencies import config, getPasswordHash
from src.schemes import User


logger = getLogger(__name__)


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    salt: str
    disabled: bool
    type: int


class Locations(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    image: str = ""
    parent : Optional[int] = Field(default=None)


class Parts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    stock: int = 0
    minStock: int = 0
    image: str = ""
    datasheet: str = ""


class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    partId: int = Field(foreign_key="parts.id")
    locationId: int = Field(foreign_key="locations.id")
    stock: int = 0


class Images(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    path: str


class Datasheets(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    path: str


def getUser(username: str) -> tuple[User, str] | None:
    """
    Get a user from the database by username.
    """
    with Session(engine) as session:
        stmt = select(Users).where(Users.username == username)
        result = session.exec(stmt)
        user = result.first()
        if user is None:
            return None
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is disabled",
                headers={"WWW-Authenticate": "Bearer"}
            )
        simpleUser = User(
            username=user.username,
            password=user.password,
            disabled=user.disabled,
            type=user.type
        )
        return simpleUser, user.salt


engine = None
match config.dbType:
    case "sqlite":
        engine = create_engine(f"sqlite:///data/{config.dbFile}")

    case _:
        logger.warning(f"Unknown database type: {config.dbType}")

if engine is not None:
    SQLModel.metadata.create_all(engine)
    logger.info("Database created")
    with Session(engine) as session:
        stmt = select(Users).where(Users.username == "admin")
        result = session.exec(stmt)
        user = result.first()
        if user is None:
            logger.warning("Admin user not found, creating default admin user")
            salt = b64encode(os.urandom(16)).decode()
            hashedPassword = getPasswordHash("admin", salt)
            newUser = Users(
                username="admin",
                password=hashedPassword,
                salt=salt,
                disabled=False,
                type=1
            )
            session.add(newUser)
            session.commit()
            logger.info("Default admin user created")
else:
    logger.critical("No engine available, exiting")
    exit(1)
