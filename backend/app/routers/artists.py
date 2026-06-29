from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import ArtistDetail
from app.services.artist_cache import get_or_create_artist, to_artist_detail

router = APIRouter()


@router.get("/artists/{slug}", response_model=ArtistDetail)
async def get_artist(slug: str, session: AsyncSession = Depends(get_db)) -> ArtistDetail:
    try:
        artist = await get_or_create_artist(session, slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return to_artist_detail(artist)
