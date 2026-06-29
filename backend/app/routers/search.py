from fastapi import APIRouter

from app.schemas import ArtistSearchResult
from app.services import discogs
from app.services.slugs import make_artist_slug

router = APIRouter()


@router.get("/search", response_model=list[ArtistSearchResult])
async def search_artists(q: str) -> list[ArtistSearchResult]:
    results = await discogs.search_artists(q)
    return [
        ArtistSearchResult(
            discogs_id=result["id"],
            name=result["title"],
            slug=make_artist_slug(result["id"], result["title"]),
            thumb=result.get("thumb") or None,
        )
        for result in results
    ]
