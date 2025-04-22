# Import built-in modules
import yaml
import logging
import logging.handlers
import logging.config
from pathlib import Path
# Import third-party modules
from coloredlogs import install

# Configer Logging
with open("logger.yaml") as f:
    # Load config
    loggerConfig = yaml.safe_load(f.read())
    # Check folder path
    logPath = Path.cwd() / Path(loggerConfig["handlers"].get("rotating")["filename"])
    logPath.parent.mkdir(parents=True, exist_ok=True)
    # Configer logging
    logging.config.dictConfig(loggerConfig)
    # Get config for color logging
    logFormat = loggerConfig.get("formatters", {}).get("simple", {}).get("format", None)
    logDatefmt = loggerConfig.get("formatters", {}).get("simple", {}).get("datefmt", None)
    logLevel = loggerConfig.get("root", {}).get("level", 0)
    # Make logging colerfull in the terminal
    install(level=logLevel, fmt=logFormat, datefmt=logDatefmt)

# Get logger
logger = logging.getLogger(__name__)
# Do rollover
for handler in logger.handlers:
    if isinstance(handler, logging.handlers.RotatingFileHandler):
        handler.doRollover()
