from logging import getLogger
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = getLogger(__name__)


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


configPath = Path("data/config.json")
if not configPath.exists():
    logger.warning("Config file not found. Creating default config.")
    with open(configPath, "w") as f:
        config = Config()
        f.write(config.model_dump_json(indent=4))
        logger.info("Default config created")

with open("config/config.json", "r") as f:
    config = Config.model_validate_json(f.read())
    logger.info("Config loaded")
