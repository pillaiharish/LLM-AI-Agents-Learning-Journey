from fastapi import APIRouter
from pydantic import BaseModel

from app.storage_analyzer.analyzer import StorageAnalyzer

router = APIRouter(prefix="/api/storage-analyzer")


class ScanRequest(BaseModel):
    path: str = "/"


@router.post("/scan")
async def scan_storage(req: ScanRequest):
    return StorageAnalyzer.analyze(req.path)
