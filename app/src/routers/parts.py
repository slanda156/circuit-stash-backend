from logging import getLogger

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

import src.database as db


logger = getLogger(__name__)
router = APIRouter()


@router.get("")
def getParts() -> dict:
    parts = {}
    with Session(db.engine) as session:
        stmt = select(db.Parts)
        result = session.exec(stmt)
        for part in result:
            parts[part.id] = {
                "name": part.name,
                "description": part.description,
                "stock": part.stock,
                "minStock": part.minStock,
                "image": part.image,
                "datasheet": part.datasheet
            }
    return parts


@router.get("/{partId}")
def getPart(partId: int) -> dict:
    if type(partId) is not int:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="partId must be integer",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if partId <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="partId must be positive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    with Session(db.engine) as session:
        stmt = select(db.Parts).where(db.Parts.id == partId)
        result = session.exec(stmt)
        part = result.first()
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No part was found with the id: {partId}",
                headers={"WWW-Authenticate": "Bearer"}
            )
    return  {
        "name": part.name,
        "description": part.description,
        "stock": part.stock,
        "minStock": part.minStock,
        "image": part.image,
        "datasheet": part.datasheet
    }


@router.post("/{partId}")
def addPart(partName: str) -> None:
    pass


@router.put("/{partId}")
def updatePart(partName: str) -> None:
    pass
