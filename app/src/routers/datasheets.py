from logging import getLogger
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

import src.database as db


logger = getLogger(__name__)
router = APIRouter()

