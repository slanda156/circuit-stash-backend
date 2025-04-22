from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: Optional[int]
    username: str
    password: bytes
    salt: bytes
    disabled: bool
    level: int
