import uuid
import io
from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from PIL import Image

import src.database as db


logger = getLogger(__name__)
router = APIRouter()


@router.get("/")
async def getImages() -> dict:
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
            images[image.id] = {
                "path": path
            }
    return images


@router.post("/")
async def addImage(image: UploadFile = File(...)) -> dict:
    if not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    filename = image.filename
    if filename:
        if not filename.endswith((".png", ".jpg", ".jpeg", ".svg")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file must be a PNG, JPG, JPEG or SVG",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    path = Path("data/images") / filename
    if path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file already exists",
            headers={"WWW-Authenticate": "Bearer"}
        )
    imageStream = io.BytesIO(await image.read())
    img = Image.open(imageStream)
    img = img.resize((50, 50))
    img.save(path)
    with Session(db.engine) as session:
        dbImage = db.Images(path=str(path))
        session.add(dbImage)
        session.commit()
        session.refresh(dbImage)
    return {"id": str(dbImage.id)}


@router.get("/{imageId}")
async def getImage(imageId: str) -> FileResponse:
    imageUUID = uuid.UUID(str(imageId), version=4)
    with Session(db.engine) as session:
        stmt = select(db.Images).where(db.Images.id == imageUUID)
        result = session.exec(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image was found with the id: {imageUUID}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if len(result.path) <= 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image was found with the id: {imageUUID}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    path = Path.cwd() / result.path
    if not path.exists():
        logger.warning(f"Image not found: {path}")
        # Send default missing png
        path = Path.cwd() / "assets" / "images" / "file-x.svg"
    return FileResponse(path, media_type=path.suffix[1:], filename=path.name)
