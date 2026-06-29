import httpx
from fastapi import APIRouter, HTTPException

from app.schemas import ReleaseDetail
from app.services.release_detail import get_release_detail

router = APIRouter()


@router.get("/releases/{mbid}", response_model=ReleaseDetail)
async def get_release(mbid: str) -> ReleaseDetail:
    try:
        return await get_release_detail(mbid)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (400, 404):
            raise HTTPException(status_code=404, detail=f"No release group with id {mbid}")
        raise
