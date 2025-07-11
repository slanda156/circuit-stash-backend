import uuid
from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

import src.database as db
from src.dependencies import getCurrentUser, validateLocation
from src.schemes import User, Location


logger = getLogger(__name__)
router = APIRouter()


@router.get("")
def getLocations(user: Annotated[User, Depends(getCurrentUser)]) -> dict:
    locations: dict[uuid.UUID, dict] = {}
    with Session(db.engine) as session:
        stmt = select(db.Locations)
        result = session.exec(stmt)
        for location in result:
            locations[location.id] = {
                "name": location.name,
                "description": location.description,
                "image": location.image,
                "parts": [],
            }
            if location.parent:
                locations[location.id]["parent"] = location.parent
            else:
                locations[location.id]["parent"] = None
        for location in locations.keys():
            stmt = select(db.Inventory).where(db.Inventory.locationId == location)
            inv_result = session.exec(stmt).all()
            for inv in inv_result:
                locations[location]["parts"].append((inv.partId, inv.stock))
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
def addLocation(location: Annotated[Location, Depends(validateLocation)],user: Annotated[User, Depends(getCurrentUser)]) -> None:
    if location.name is None or location.name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location name is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    with Session(db.engine) as session:
        imageId = None
        if location.image is not None:
            imageId = location.image
            stmt = select(db.Images).where(db.Images.id == imageId)
            result = session.exec(stmt)
            exisistingImage = result.first()
            if not exisistingImage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Image with name {location.image} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if exisistingImage.id is not None:
                imageId = exisistingImage.id

        if location.description is None:
            location.description = ""

        if location.parent is not None:
            stmt = select(db.Locations).where(db.Locations.id == location.parent)
            result = session.exec(stmt)
            existingParent = result.first()
            if not existingParent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent location with id {location.parent} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )

        if location.id is not None:
            stmt = select(db.Locations).where(db.Locations.id == location.id)
            result = session.exec(stmt)
            existingLocation = result.first()
            if existingLocation:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Location with id {location.id} already exists",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            newLocation = db.Locations(
                id=location.id,
                name=location.name,
                description=location.description,
                image=imageId,
                parent=location.parent
            )

        else:
            newLocation = db.Locations(
                name=location.name,
                description=location.description,
                image=imageId,
                parent=location.parent
            )

        session.add(newLocation)
        session.commit()


@router.put("/")
def updateLocation(location: Annotated[Location, Depends(validateLocation)], user: Annotated[User, Depends(getCurrentUser)]) -> None:
    with Session(db.engine) as session:
        stmt = select(db.Locations).where(db.Locations.id == location.id)
        result = session.exec(stmt)
        existingLocation = result.first()
        if not existingLocation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No location was found with the id: {location.id}",
                headers={"WWW-Authenticate": "Bearer"}
            )

        existingLocation.name = location.name

        if location.description is not None:
            existingLocation.description = location.description

        if location.image is not None:
            stmt = select(db.Images).where(db.Images.id == location.image)
            result = session.exec(stmt)
            existingImage = result.first()
            if not existingImage:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image with name {location.image} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            existingLocation.image = existingImage.id

        if location.parent is not None:
            stmt = select(db.Locations).where(db.Locations.id == location.parent)
            result = session.exec(stmt)
            existingParent = result.first()
            if not existingParent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent location with id {location.parent} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            existingLocation.parent = existingParent.id

        session.add(existingLocation)
        session.commit()
