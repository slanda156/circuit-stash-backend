#!/usr/bin/env python3
# Import built-in modules
import logging
# Import third-party modules
import uvicorn
from fastapi import FastAPI
# Import local modules
from src import loggerConfig
from src.routers import admin, user, parts, locations, images, datasheets
from src.dependencies import VERSION

logger = logging.getLogger(__name__)

# Define the FastAPI app
app = FastAPI(
    title="Circuit Stash API",
    description="API for Circuit Stash",
    version=VERSION,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai"
    }
)
# Include the routers
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)
app.include_router(
    user.router,
    prefix="/user",
    tags=["user"]
)
app.include_router(
    parts.router,
    prefix="/parts",
    tags=["parts"]
)
app.include_router(
    locations.router,
    prefix="/locations",
    tags=["locations"]
)
app.include_router(
    images.router,
    prefix="/images",
    tags=["images"]
)
app.include_router(
    datasheets.router,
    prefix="/datasheets",
    tags=["datasheets"]
)

# Define the main function
def main() -> None:
    logger.info(f"Starting the circuit stash backend {VERSION}")
    logger.info(f"Loaded {len(app.routes)} routes")
    for route in app.routes:
        logger.debug(f"Route: \"{route.path}\" - Methods: {route.methods}") # type: ignore
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=loggerConfig
    )
    logger.info("Server stopped")


# Run the program if it is the main module
if __name__ == "__main__":
    try:
        main()
    # Log any exceptions
    except Exception:
        logger.critical("An unhandled exception occurred:", exc_info=True)
        raise
