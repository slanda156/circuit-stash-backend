from logging import getLogger

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

import src.database as db


logger = getLogger(__name__)
router = APIRouter()


@router.get("")
def getLocations() -> dict:
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
