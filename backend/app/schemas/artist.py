from pydantic import BaseModel, Field


class ArtistSearchResult(BaseModel):
    discogs_id: int
    name: str
    slug: str
    thumb: str | None = None


class ReleaseOut(BaseModel):
    title: str
    year: int | None = None
    musicbrainz_id: str | None = None


class ArtistDetail(BaseModel):
    name: str
    slug: str
    image_url: str | None = None
    location: str | None = None
    years_active: str | None = None
    members: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    bio: str | None = None
    releases: dict[str, list[ReleaseOut]]
