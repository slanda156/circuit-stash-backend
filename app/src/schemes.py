import uuid

from pydantic import BaseModel


class User(BaseModel):
    """
    User model for the application.
    """
    username: str
    password: str | None = None
    disabled: bool | None = None
    type: int | None = None


class Token(BaseModel):
    """
    Token model for the application.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Token data model for the application.
    """
    username: str
    type: int
    expiration: float


class Part(BaseModel):
    """
    Part model for the application.
    """
    id: uuid.UUID | None = None
    name: str
    description: str | None = None
    minStock: int | None = None
    image: uuid.UUID | None = None
    datasheet: uuid.UUID | None = None


class Location(BaseModel):
    """
    Location model for the application.
    """
    id: uuid.UUID | None = None
    name: str
    description: str | None = None
    image: uuid.UUID | None = None
    parent: uuid.UUID | None = None


class Image(BaseModel):
    """
    Image model for the application.
    """
    id: uuid.UUID | None = None
    path: str


class Datasheet(BaseModel):
    """
    Datasheet model for the application.
    """
    id: uuid.UUID | None = None
    path: str | None = None
