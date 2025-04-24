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
