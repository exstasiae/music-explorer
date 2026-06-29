import time

import httpx

from app.config import settings

_token: str | None = None
_token_expires_at: float = 0.0


async def _get_token() -> str:
    global _token, _token_expires_at
    if _token and time.monotonic() < _token_expires_at:
        return _token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(settings.spotify_client_id, settings.spotify_client_secret),
        )
        response.raise_for_status()
        payload = response.json()
    _token = payload["access_token"]
    _token_expires_at = time.monotonic() + payload["expires_in"] - 60
    return _token


async def get_artist_info(name: str) -> dict:
    token = await _get_token()
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
        response = await client.get(
            "https://api.spotify.com/v1/search",
            params={"q": name, "type": "artist", "limit": 1},
        )
        response.raise_for_status()
        items = response.json()["artists"]["items"]
    if not items:
        return {"image_url": None, "genres": []}
    artist = items[0]
    images = artist.get("images") or []
    return {
        "image_url": images[0]["url"] if images else None,
        "genres": artist.get("genres", []),
    }
