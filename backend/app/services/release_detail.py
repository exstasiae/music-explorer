from app.schemas import ListenLinkOut, PersonnelGroup, ReleaseDetail, TrackOut
from app.services import musicbrainz

LISTEN_RELATION_TYPES = {"free streaming", "streaming"}

LINK_DOMAINS = {
    "open.spotify.com": "Spotify",
    "music.apple.com": "Apple Music",
    "itunes.apple.com": "Apple Music",
    "tidal.com": "Tidal",
    "deezer.com": "Deezer",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "bandcamp.com": "Bandcamp",
    "soundcloud.com": "SoundCloud",
}


def _service_for_url(url: str) -> str | None:
    for domain, service in LINK_DOMAINS.items():
        if domain in url:
            return service
    return None


def _format_duration(ms: int | None) -> str | None:
    if not ms:
        return None
    seconds = round(ms / 1000)
    return f"{seconds // 60}:{seconds % 60:02d}"


def _pick_release(releases: list[dict]) -> dict | None:
    official = [r for r in releases if r.get("status") == "Official"]
    pool = official or releases
    for release in pool:
        if release.get("country") == "XW":
            return release
    return pool[0] if pool else None


def _pick_earliest_official(releases: list[dict], exclude_id: str) -> dict | None:
    official = [r for r in releases if r.get("status") == "Official" and r.get("id") != exclude_id]
    dated = [r for r in official if r.get("date")]
    if not dated:
        return None
    return min(dated, key=lambda r: r["date"])


def _extract_tracks(release: dict) -> tuple[list[TrackOut], int]:
    tracks: list[TrackOut] = []
    total_ms = 0
    for medium in release.get("media") or []:
        for track in medium.get("tracks") or []:
            credits = track.get("artist-credit") or []
            features = [credit["artist"]["name"] for credit in credits[1:] if credit.get("artist")]
            recording = track.get("recording") or {}
            length = track.get("length") or recording.get("length")
            total_ms += length or 0
            tracks.append(
                TrackOut(
                    position=str(track.get("number") or len(tracks) + 1),
                    title=track.get("title") or recording.get("title", ""),
                    duration=_format_duration(length),
                    features=features,
                )
            )
    return tracks, total_ms


def _extract_label(release: dict) -> str | None:
    names = []
    for entry in release.get("label-info") or []:
        name = (entry.get("label") or {}).get("name")
        if name and name not in names:
            names.append(name)
    return ", ".join(names) or None


def _role_label(relation: dict) -> str:
    attributes = relation.get("attributes") or []
    role = relation.get("type", "")
    return f"{'-'.join(attributes)} {role}".strip() if attributes else role


def _extract_personnel(release: dict) -> list[PersonnelGroup]:
    order: list[str] = []
    names_by_role: dict[str, list[str]] = {}

    def add(relation: dict) -> None:
        artist = relation.get("artist")
        if not artist or not artist.get("name"):
            return
        role = _role_label(relation)
        if role not in names_by_role:
            order.append(role)
            names_by_role[role] = []
        if artist["name"] not in names_by_role[role]:
            names_by_role[role].append(artist["name"])

    for relation in release.get("relations") or []:
        if relation.get("target-type") == "artist":
            add(relation)

    for medium in release.get("media") or []:
        for track in medium.get("tracks") or []:
            recording = track.get("recording") or {}
            for relation in recording.get("relations") or []:
                if relation.get("target-type") == "artist":
                    add(relation)

    return [PersonnelGroup(role=role, names=names_by_role[role]) for role in order]


def _extract_links(release: dict) -> list[ListenLinkOut]:
    links: list[ListenLinkOut] = []
    seen_services: set[str] = set()
    for relation in release.get("relations") or []:
        if relation.get("type") not in LISTEN_RELATION_TYPES:
            continue
        url = (relation.get("url") or {}).get("resource")
        if not url:
            continue
        service = _service_for_url(url)
        if not service or service in seen_services:
            continue
        seen_services.add(service)
        links.append(ListenLinkOut(service=service, url=url))
    return links


async def get_release_detail(mbid: str) -> ReleaseDetail:
    group = await musicbrainz.get_release_group_detail(mbid)
    release_stub = _pick_release(group.get("releases") or [])

    tracks: list[TrackOut] = []
    links: list[ListenLinkOut] = []
    personnel: list[PersonnelGroup] = []
    label = None
    total_duration = None
    release_date = group.get("first-release-date")

    if release_stub is not None:
        release = await musicbrainz.get_release(release_stub["id"])
        release_date = release.get("date") or release_date
        label = _extract_label(release)
        tracks, total_ms = _extract_tracks(release)
        total_duration = _format_duration(total_ms)
        links = _extract_links(release)
        personnel = _extract_personnel(release)

        if not personnel:
            fallback_stub = _pick_earliest_official(group.get("releases") or [], release_stub["id"])
            if fallback_stub is not None:
                fallback_release = await musicbrainz.get_release(fallback_stub["id"])
                personnel = _extract_personnel(fallback_release)

    return ReleaseDetail(
        musicbrainz_id=mbid,
        title=group.get("title", ""),
        release_type=musicbrainz.categorize_group(group),
        release_date=release_date,
        label=label,
        cover_url=f"https://coverartarchive.org/release-group/{mbid}/front-1200",
        genres=musicbrainz.top_genres(group),
        tracks=tracks,
        total_duration=total_duration,
        links=links,
        personnel=personnel,
    )
