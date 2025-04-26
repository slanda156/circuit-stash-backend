from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

import src.database as db


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
                "name": datasheet.name,
                "path": path
            }
    return datasheets


@router.get("/{datasheetName}")
def getDatasheet(datasheetName: str) -> FileResponse:
    with Session(db.engine) as session:
        stmt = select(db.Datasheets).where(db.Datasheets.name == datasheetName)
        result = session.exec(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No datasheet was found with the name: {datasheetName}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if len(result.path) <= 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No datasheet was found with the name: {datasheetName}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    path = Path(result.path)
    if not path.exists():
        logger.warning(f"Datasheet not found: {path}")
        # Send default missing png
        path = Path.cwd() / "assets" / "images" / "file-x.svg"
    return FileResponse(path, media_type=path.suffix[1:], filename=path.name)
