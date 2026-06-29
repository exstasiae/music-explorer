import httpx

from app.config import settings

BASE_URL = "https://api.genius.com"

JUNK_DESCRIPTIONS = {"?", "...", "-", ""}


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.genius_token}"}


def _flatten_dom(node) -> str:
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    text = "".join(_flatten_dom(child) for child in node.get("children") or [])
    if node.get("tag") == "p":
        return text + "\n\n"
    if node.get("tag") == "br":
        return text + "\n"
    return text


async def search_artist(name: str) -> dict | None:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=10.0) as client:
        response = await client.get("/search", params={"q": name})
        response.raise_for_status()
        hits = response.json()["response"]["hits"]
    name_lower = name.lower()
    for hit in hits:
        primary_artist = hit["result"]["primary_artist"]
        if primary_artist["name"].lower() == name_lower:
            return primary_artist
    return None


async def get_artist_description(artist_id: int) -> str | None:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=10.0) as client:
        response = await client.get(f"/artists/{artist_id}")
        response.raise_for_status()
        artist = response.json()["response"]["artist"]
    dom = (artist.get("description") or {}).get("dom")
    if not dom:
        return None
    text = _flatten_dom(dom).strip()
    return text or None


async def get_artist_bio(name: str) -> str | None:
    try:
        artist = await search_artist(name)
        if artist is None:
            return None
        description = await get_artist_description(artist["id"])
    except (httpx.HTTPError, KeyError, TypeError):
        return None
    if description and description.strip() not in JUNK_DESCRIPTIONS:
        return description
    return None
