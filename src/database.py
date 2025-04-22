from sqlmodel import Field, SQLModel, create_engine
from typing import Optional


engine = create_engine("mysql+pymysql://bot:pw@127.0.0.1:3306/userdb")


class User(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, description="User ID")
    username: str
    password: bytes
    salt: bytes
    disabled: bool
    level: int
