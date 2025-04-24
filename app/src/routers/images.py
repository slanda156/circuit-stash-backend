from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

import src.database as db


logger = getLogger(__name__)
router = APIRouter()


@router.get("/")
def getImages() -> dict:
    images = {}
    with Session(db.engine) as session:
        stmt = select(db.Images)
        result = session.exec(stmt)
        for image in result:
            pathParts = Path(image.path).as_posix().split("/")
            for part in pathParts:
                pathParts.pop(0)
                if part == "data":
                    break
            path = "/".join(pathParts)
            logger.debug(f"Image path: {path}")
            images[image.id] = {
                "name": image.name,
                "path": path
            }
    return images


@router.get("/{imageId}")
def getImage(imageId: int) -> FileResponse:
    with Session(db.engine) as session:
        stmt = select(db.Images).where(db.Images.id == imageId)
        result = session.exec(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image was found with the id: {imageId}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if len(result.path) <= 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image was found with the id: {imageId}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    path = Path(result.path)
    if not path.exists():
        logger.warning(f"Image not found: {path}")
        # Send default missing png
        path = Path.cwd() / "assets" / "images" / "file-x.svg"
    return FileResponse(path, media_type=path.suffix[1:], filename=path.name)
