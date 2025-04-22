from logging import getLogger
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine

from src.config import config


logger = getLogger(__name__)

engine = None
match config.dbType:
    case "sqlite":
        engine = create_engine(f"sqlite:///data/{config.dbFile}")

    case _:
        logger.warning(f"Unknown database type: {config.dbType}")

if engine is not None:
    SQLModel.metadata.create_all(engine)
else:
    logger.critical("No engine available, exiting")
    exit(1)


class Users(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, description="User ID")
    username: str
    password: bytes
    salt: bytes
    disabled: bool
    type: int
