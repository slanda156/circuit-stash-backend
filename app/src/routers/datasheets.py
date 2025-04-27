import uuid
import shutil
from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session, select

import src.database as db
from src.schemes import Datasheet


logger = getLogger(__name__)
router = APIRouter()

@router.get("/")
def getDatasheets() -> dict:
    datasheets = {}
    with Session(db.engine) as session:
        stmt = select(db.Datasheets)
        result = session.exec(stmt)
        for datasheet in result:
            pathParts = Path(datasheet.path).as_posix().split("/")
            for part in pathParts:
                pathParts.pop(0)
                if part == "data":
                    break
            path = "/".join(pathParts)
            logger.debug(f"Datasheet path: {path}")
            datasheets[datasheet.id] = {
                "path": path
            }
    return datasheets


@router.post("/")
def addDatasheet(datasheet: UploadFile = File(...)) -> dict:
    if not datasheet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datasheet file is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    filename = datasheet.filename
    if filename:
        if not filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datasheet file must be a PDF",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datasheet file is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    path = Path("data/datasheets") / filename
    if path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datasheet file already exists",
            headers={"WWW-Authenticate": "Bearer"}
        )
    with open(path, "wb") as f:
        shutil.copyfileobj(datasheet.file, f)
    with Session(db.engine) as session:
        dbDatasheet = db.Datasheets(path=str(path))
        session.add(dbDatasheet)
        session.commit()
        session.refresh(dbDatasheet)
    return {"id": str(dbDatasheet.id)}


@router.get("/{datasheetId}")
def getDatasheet(datasheetId: str) -> FileResponse:
    datasheetUUID = uuid.UUID(str(datasheetId), version=4)
    with Session(db.engine) as session:
        stmt = select(db.Datasheets).where(db.Datasheets.id == datasheetUUID)
        result = session.exec(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No datasheet was found with the id: {datasheetUUID}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if len(result.path) <= 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No datasheet was found with the id: {datasheetUUID}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    path = Path(result.path)
    if not path.exists():
        logger.warning(f"Datasheet not found: {path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No datasheet was found with the id: {datasheetUUID}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return FileResponse(path, media_type="application/pdf", filename=path.name, headers={"Content-Disposition": f"inline; filename={path.name}"})
