from logging import getLogger
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine

from src.config import config


logger = getLogger(__name__)

match config.dbType:
    case "sqlite":
        engine = create_engine(f"sqlite:///{config.dbFile}")

    case _:
        logger.warning(f"Unknown database type: {config.dbType}")


class Users(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, description="User ID")
    username: str
    password: bytes
    salt: bytes
    disabled: bool
    type: int
