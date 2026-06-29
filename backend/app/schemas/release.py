from pydantic import BaseModel, Field


class TrackOut(BaseModel):
    position: str
    title: str
    duration: str | None = None
    features: list[str] = Field(default_factory=list)


class ListenLinkOut(BaseModel):
    service: str
    url: str


class PersonnelGroup(BaseModel):
    role: str
    names: list[str]


class ReleaseDetail(BaseModel):
    musicbrainz_id: str
    title: str
    release_type: str
    release_date: str | None = None
    label: str | None = None
    cover_url: str
    genres: list[str] = Field(default_factory=list)
    tracks: list[TrackOut] = Field(default_factory=list)
    total_duration: str | None = None
    links: list[ListenLinkOut] = Field(default_factory=list)
    personnel: list[PersonnelGroup] = Field(default_factory=list)
