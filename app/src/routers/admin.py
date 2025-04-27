import os
from logging import getLogger
from pathlib import Path
from typing import Annotated
from base64 import b64encode

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

import src.database as db
from src.dependencies import getPasswordHash, isAdmin
from src.schemes import User


logger = getLogger(__name__)
router = APIRouter()


@router.get("/users")
def getusers(user: Annotated[User, Depends(isAdmin)]) -> dict:
    return {}


@router.get("/users/user")
def getUserByName(user: Annotated[User, Depends(isAdmin)], username: str) -> dict:
    return {}


@router.post("/user/user")
def addUser(user: Annotated[User, Depends(isAdmin)], username: str, password: str, type: int) -> None:
    if db.getUser(username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
            headers={"WWW-Authenticate": "Bearer"}
        )
    salt = b64encode(os.urandom(16)).decode()
    hashedPassword = getPasswordHash(password, salt)
    with Session(db.engine) as session:
        newUser = db.Users(
            username=username,
            password=hashedPassword,
            salt=salt,
            disabled=False,
            type=type
        )
        session.add(newUser)
        session.commit()


@router.put("/users/user")
def changeUser(user: Annotated[User, Depends(isAdmin)], changedUser: User) -> None:
    pass


@router.delete("/users/user")
def deleteUser(user: Annotated[User, Depends(isAdmin)], username: str) -> None:
    pass


@router.get("/configs")
def getConfigs(user: Annotated[User, Depends(isAdmin)]) -> dict:
    return {}


@router.get("/configs/{name}")
def getConfig(user: Annotated[User, Depends(isAdmin)], name: str) -> dict:
    return {}


@router.post("/configs")
def addConfig(user: Annotated[User, Depends(isAdmin)], name: str, value: str) -> None:
    pass


@router.post("/images")
def reloadImages(user: Annotated[User, Depends(isAdmin)]) -> None:
    logger.warning("Reloading images")
    with Session(db.engine) as session:
        stmt = select(db.Images)
        result = session.exec(stmt)
        images = result.all()
        for image in images:
            session.delete(image)
        imagePath = Path("data/images")
        imageExtensions = ["png", "jpg", "jpeg"]
        images = []
        for extension in imageExtensions:
            images.extend(imagePath.glob(f"*.{extension}"))
        for image in images:
            newImage = db.Images(path=str(imagePath / image.name))
            session.add(newImage)
        logger.info(f"Added {len(images)} images")
        session.commit()


@router.post("/datasheets")
def reloadDatasheets(user: Annotated[User, Depends(isAdmin)]) -> None:
    logger.warning("Reloading datasheets")
    with Session(db.engine) as session:
        stmt = select(db.Datasheets)
        result = session.exec(stmt)
        datasheets = result.all()
        for datasheet in datasheets:
            session.delete(datasheet)
        datasheetPath = Path("data/datasheets")
        datasheets = list(datasheetPath.glob("*.pdf"))
        for datasheet in datasheets:
            newDatasheet = db.Datasheets(path=str(datasheetPath / datasheet.name))
            session.add(newDatasheet)
        logger.info(f"Added {len(datasheets)} datasheets")
        session.commit()
