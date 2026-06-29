import asyncio
import time

import httpx

BASE_URL = "https://musicbrainz.org/ws/2"
USER_AGENT = "MusicExplorer/0.1 ( https://github.com/foskettg/music-explorer )"

_last_request_at = 0.0
_lock = asyncio.Lock()

RELEASE_CATEGORIES = ("Album", "Mixtape", "EP", "Compilation", "Single", "Other")


def _headers() -> dict[str, str]:
    return {"User-Agent": USER_AGENT}


async def _throttled_get(client: httpx.AsyncClient, url: str, params: dict) -> httpx.Response:
    global _last_request_at
    while True:
        async with _lock:
            elapsed = time.monotonic() - _last_request_at
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
            _last_request_at = time.monotonic()
        response = await client.get(url, params=params)
        if response.status_code in (429, 503):
            await asyncio.sleep(float(response.headers.get("Retry-After", 2)))
            continue
        response.raise_for_status()
        return response


async def search_artist(name: str, min_score: int = 90) -> dict | None:
    """Match by current name or by alias/former name.

    Artists who have legally or professionally renamed (e.g. Kanye West -> Ye)
    get their old name demoted to an alias in MusicBrainz, with a different
    artist as the current "name" field. Searching only `artist:"..."` misses
    them entirely and can match an unrelated tribute/parody act instead.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=20.0) as client:
        response = await _throttled_get(
            client,
            "/artist",
            {"query": f'artist:"{name}" OR alias:"{name}"', "fmt": "json", "limit": 5},
        )
        artists = response.json().get("artists", [])
    if not artists or artists[0].get("score", 0) < min_score:
        return None
    return artists[0]


async def get_release_groups(mbid: str) -> list[dict]:
    """Release groups with at least one Official release, deduped.

    Browsing /release-group directly has no release-status info, so a release
    group whose only releases are bootlegs/promos looks identical to a real
    album. Browsing /release instead exposes each release's status, which is
    what musicbrainz.org's own artist Overview page filters on.
    """
    groups: dict[str, dict] = {}
    offset = 0
    limit = 100
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=20.0) as client:
        while True:
            response = await _throttled_get(
                client,
                "/release",
                {"artist": mbid, "fmt": "json", "limit": limit, "offset": offset, "inc": "release-groups"},
            )
            payload = response.json()
            for release in payload["releases"]:
                if release.get("status") != "Official":
                    continue
                group = release["release-group"]
                groups.setdefault(group["id"], group)
            total = payload.get("release-count", offset + len(payload["releases"]))
            offset += limit
            if offset >= total:
                break
    return list(groups.values())


def _format_members(relations: list[dict]) -> list[str]:
    order: list[str] = []
    currently_active: dict[str, bool] = {}
    for rel in relations:
        if rel.get("type") != "member of band":
            continue
        name = (rel.get("artist") or {}).get("name")
        if not name:
            continue
        if name not in currently_active:
            order.append(name)
            currently_active[name] = False
        if not rel.get("ended"):
            currently_active[name] = True
    return [name if currently_active[name] else f"{name} (former)" for name in order]


def _format_location(data: dict) -> str | None:
    area = data.get("area") or {}
    begin_area = data.get("begin-area") or {}
    names = []
    for place in (begin_area, area):
        name = place.get("name")
        if name and name not in names:
            names.append(name)
    return ", ".join(names) or None


def _format_years_active(data: dict) -> str | None:
    life_span = data.get("life-span") or {}
    begin = life_span.get("begin")
    if not begin:
        return None
    begin_year = begin[:4]
    end = life_span.get("end")
    if end:
        return f"{begin_year}–{end[:4]}"
    if life_span.get("ended"):
        return f"{begin_year}–?"
    return f"{begin_year}–present"


def top_genres(data: dict, limit: int = 3) -> list[str]:
    genres = sorted(data.get("genres") or [], key=lambda g: g.get("count", 0), reverse=True)
    return [genre["name"] for genre in genres[:limit]]


async def get_artist_details(mbid: str) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=20.0) as client:
        response = await _throttled_get(
            client, f"/artist/{mbid}", {"inc": "artist-rels+genres", "fmt": "json"}
        )
        data = response.json()
    is_group = data.get("type") == "Group"
    return {
        "location": _format_location(data),
        "years_active": _format_years_active(data) if is_group else None,
        "members": _format_members(data.get("relations") or []) if is_group else [],
        "genres": top_genres(data),
    }


def categorize_group(group: dict) -> str:
    primary = group.get("primary-type")
    secondary = set(group.get("secondary-types") or [])
    if "Compilation" in secondary:
        return "Compilation"
    if "Mixtape/Street" in secondary:
        return "Mixtape"
    if primary == "Album" and not secondary:
        return "Album"
    if primary == "EP" and not secondary:
        return "EP"
    if primary == "Single" and not secondary:
        return "Single"
    return "Other"


def categorize_release_groups(groups: list[dict]) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = {category: [] for category in RELEASE_CATEGORIES}
    for group in groups:
        buckets[categorize_group(group)].append(group)
    return buckets


async def get_release_group_detail(mbid: str) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=20.0) as client:
        response = await _throttled_get(
            client, f"/release-group/{mbid}", {"inc": "genres+releases", "fmt": "json"}
        )
        return response.json()


async def get_release(release_id: str) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=20.0) as client:
        response = await _throttled_get(
            client,
            f"/release/{release_id}",
            {
                "inc": "recordings+artist-credits+url-rels+artist-rels+recording-rels+labels",
                "fmt": "json",
            },
        )
        return response.json()
