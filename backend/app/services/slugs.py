import re


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "artist"


def make_artist_slug(discogs_id: int, name: str) -> str:
    return f"{discogs_id}-{slugify(name)}"


def discogs_id_from_slug(slug: str) -> int:
    return int(slug.split("-", 1)[0])
