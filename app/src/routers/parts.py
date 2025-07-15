import uuid
from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

import src.database as db
from src.dependencies import getCurrentUser, validatePart
from src.schemes import User, Part


logger = getLogger(__name__)
router = APIRouter()


@router.get("/")
async def getParts(user: Annotated[User, Depends(getCurrentUser)]) -> dict:
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
async def getPart(partId: uuid.UUID, user: Annotated[User, Depends(getCurrentUser)]) -> dict:
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


@router.post("/")
async def addPart(part: Annotated[Part, Depends(validatePart)], user: Annotated[User, Depends(getCurrentUser)]) -> None:
    if part.minStock is None or part.minStock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Part minStock is required and must be positive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if part.name is None or part.name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Part name is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    with Session(db.engine) as session:
        imageId = None
        if part.image is not None:
            stmt = select(db.Images).where(db.Images.id == part.image)
            result = session.exec(stmt)
            existingImage = result.first()
            if not existingImage:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image with name {part.image} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if existingImage.id is not None:
                imageId = existingImage.id
        datasheetId = None
        if part.datasheet is not None:
            stmt = select(db.Datasheets).where(db.Datasheets.id == part.datasheet)
            result = session.exec(stmt)
            existingDatasheet = result.first()
            if not existingDatasheet:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Datasheet with name {part.datasheet} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if existingDatasheet.id is not None:
                datasheetId = existingDatasheet.id
        if part.description is None:
            part.description = ""
        if part.id is not None:
            stmt = select(db.Parts).where(db.Parts.id == part.id)
            result = session.exec(stmt)
            existingPart = result.first()
            if existingPart:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Part with id {part.id} already exists",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            newPart = db.Parts(
                id=part.id,
                name=part.name,
                description=part.description,
                stock=0,
                minStock=part.minStock,
                image=imageId,
                datasheet=datasheetId
            )
        else:
            newPart = db.Parts(
                name=part.name,
                description=part.description,
                stock=0,
                minStock=part.minStock,
                image=imageId,
                datasheet=datasheetId
            )
        session.add(newPart)
        session.commit()

@router.put("/")
async def updatePart(part: Annotated[Part, Depends(validatePart)], user: Annotated[User, Depends(getCurrentUser)]) -> None:
    with Session(db.engine) as session:
        stmt = select(db.Parts).where(db.Parts.id == part.id)
        result = session.exec(stmt)
        existingPart = result.first()
        if not existingPart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No part was found with the id: {part.id}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        existingPart.name = part.name
        if part.description is not None:
            existingPart.description = part.description
        if part.minStock is not None:
            existingPart.minStock = part.minStock
        if part.image is not None:
            stmt = select(db.Images).where(db.Images.id == part.image)
            result = session.exec(stmt)
            existingImage = result.first()
            if not existingImage:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image with name {part.image} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if existingImage.id is not None:
                existingPart.image = existingImage.id
        if part.datasheet is not None:
            stmt = select(db.Datasheets).where(db.Datasheets.id == part.datasheet)
            result = session.exec(stmt)
            existingDatasheet = result.first()
            if not existingDatasheet:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Datasheet with name {part.datasheet} does not exist",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if existingDatasheet.id is not None:
                existingPart.datasheet = existingDatasheet.id
        stmt = select(db.Inventory).where(db.Inventory.partId == part.id)
        result = session.exec(stmt)
        existingInventory = result.all()
        existingPart.stock = 0
        for inventory in existingInventory:
            existingPart.stock += inventory.stock
        session.add(existingPart)
        session.commit()
