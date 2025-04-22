from logging import getLogger
from pathlib import Path
from typing import Optional

import rsa
from base64 import b64decode
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

with open("data/config.json", "r") as f:
    config = Config.model_validate_json(f.read())
    logger.info("Config loaded")

secrets = {}
with open("data/secrets.json", "rb") as f:
    jwtSecret = b64decode(f.read())
secrets["jwt"] = jwtSecret

with open("data/private.key", "rb") as f:
    privateKey = rsa.PrivateKey.load_pkcs1(f.read())
secrets["privateKey"] = privateKey

with open("data/public.key", "rb") as f:
    publicKey = rsa.PublicKey.load_pkcs1(f.read())
secrets["publicKey"] = publicKey
