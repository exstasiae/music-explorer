import json
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Artist, Release
from app.schemas import ArtistDetail, ReleaseOut
from app.services import bio, discogs, genius, musicbrainz, spotify
from app.services.slugs import discogs_id_from_slug

RELEASE_CATEGORIES = musicbrainz.RELEASE_CATEGORIES


async def get_or_create_artist(session: AsyncSession, slug: str) -> Artist:
    try:
        discogs_id = discogs_id_from_slug(slug)
    except ValueError:
        raise ValueError(f"Invalid artist slug: {slug}")

    result = await session.execute(
        select(Artist).where(Artist.slug == slug).options(selectinload(Artist.releases))
    )
    artist = result.scalar_one_or_none()
    if artist is not None and artist.bio:
        return artist

    try:
        discogs_artist = await discogs.get_artist(discogs_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise ValueError(f"No Discogs artist with id {discogs_id}")
        raise

    name = discogs_artist.get("name", "")
    spotify_info = await spotify.get_artist_info(name)

    buckets: dict[str, list[dict]] = {category: [] for category in RELEASE_CATEGORIES}
    details: dict = {"location": None, "years_active": None, "members": []}
    mb_artist = await musicbrainz.search_artist(name)
    if mb_artist is not None:
        groups = await musicbrainz.get_release_groups(mb_artist["id"])
        buckets = musicbrainz.categorize_release_groups(groups)
        details = await musicbrainz.get_artist_details(mb_artist["id"])

    active_years = details.get("years_active")
    if not active_years:
        album_years = [
            int(group["first-release-date"][:4])
            for group in buckets.get("Album", [])
            if group.get("first-release-date") and group["first-release-date"][:4].isdigit()
        ]
        active_years = f"{min(album_years)}–{max(album_years)}" if album_years else None

    discogs_profile = discogs_artist.get("profile") or None
    genius_bio = None
    if not discogs_profile or len(discogs_profile) < 200:
        genius_bio = await genius.get_artist_bio(name)

    bio_text = await bio.generate_bio(
        name=name,
        discogs_profile=discogs_profile,
        genres=spotify_info.get("genres", []),
        active_years=active_years,
        genius_bio=genius_bio,
    )

    if artist is None:
        artist = Artist(slug=slug, discogs_id=discogs_id, name=name)
        session.add(artist)
    else:
        artist.name = name

    artist.image_url = spotify_info.get("image_url")
    artist.location = details.get("location")
    artist.years_active = active_years
    artist.members = json.dumps(details.get("members")) if details.get("members") else None
    artist.genres = json.dumps(details.get("genres")) if details.get("genres") else None
    artist.bio = bio_text
    artist.bio_generated_at = datetime.now(timezone.utc)

    artist.releases.clear()
    for category in RELEASE_CATEGORIES:
        for group in buckets.get(category, []):
            year = None
            date = group.get("first-release-date")
            if date and date[:4].isdigit():
                year = int(date[:4])
            artist.releases.append(
                Release(
                    musicbrainz_id=group.get("id"),
                    title=group.get("title", ""),
                    release_type=category,
                    year=year,
                )
            )

    await session.commit()
    await session.refresh(artist, attribute_names=["releases"])
    return artist


def to_artist_detail(artist: Artist) -> ArtistDetail:
    releases_by_type: dict[str, list[ReleaseOut]] = {category: [] for category in RELEASE_CATEGORIES}
    for release in artist.releases:
        releases_by_type.setdefault(release.release_type, []).append(release)
    for category, releases in releases_by_type.items():
        releases.sort(key=lambda r: (r.year is None, r.year, r.title))
        releases_by_type[category] = [
            ReleaseOut(title=r.title, year=r.year, musicbrainz_id=r.musicbrainz_id) for r in releases
        ]
    return ArtistDetail(
        name=artist.name,
        slug=artist.slug,
        image_url=artist.image_url,
        location=artist.location,
        years_active=artist.years_active,
        members=json.loads(artist.members) if artist.members else [],
        genres=json.loads(artist.genres) if artist.genres else [],
        bio=artist.bio,
        releases=releases_by_type,
    )
