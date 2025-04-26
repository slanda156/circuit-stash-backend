from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

import src.database as db
from src.dependencies import getCurrentUser
from src.schemes import User, Location


logger = getLogger(__name__)
router = APIRouter()


@router.get("")
def getLocations(user: Annotated[User, Depends(getCurrentUser)]) -> dict:
    locations = {}
    with Session(db.engine) as session:
        stmt = select(db.Locations)
        result = session.exec(stmt)
        for location in result:
            locations[location.id] = {
                "name": location.name,
                "description": location.description,
                "image": location.image
            }
            if location.parent:
                locations[location.id]["parent"] = location.parent
            else:
                locations[location.id]["parent"] = None
    return locations


@router.get("/{locationName}")
def getLocationByName(user: Annotated[User, Depends(getCurrentUser)], locationName: str) -> dict:
    with Session(db.engine) as session:
        stmt = select(db.Locations).where(db.Locations.name == locationName)
        result = session.exec(stmt).first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return {
            "name": result.name,
            "description": result.description,
            "image": result.image,
            "parent": result.parent
        }


@router.post("/")
def addLocation(, user: Annotated[User, Depends(getCurrentUser)]) -> None:
