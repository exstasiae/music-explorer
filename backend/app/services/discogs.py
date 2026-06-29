import asyncio

import httpx

from app.config import settings

BASE_URL = "https://api.discogs.com"
USER_AGENT = "MusicExplorer/0.1 +https://github.com/foskettg/music-explorer"


def _headers() -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Authorization": f"Discogs token={settings.discogs_token}",
    }


async def _get_with_rate_limit_retry(client: httpx.AsyncClient, url: str, params: dict) -> httpx.Response:
    while True:
        response = await client.get(url, params=params)
        if response.status_code != 429:
            response.raise_for_status()
            return response
        delay = float(response.headers.get("Retry-After", 5))
        await asyncio.sleep(delay)


async def search_artists(query: str, per_page: int = 10) -> list[dict]:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers()) as client:
        response = await _get_with_rate_limit_retry(
            client, "/database/search", {"q": query, "type": "artist", "per_page": per_page}
        )
        return response.json()["results"]


async def get_artist(discogs_id: int) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers()) as client:
        response = await _get_with_rate_limit_retry(client, f"/artists/{discogs_id}", {})
        return response.json()
