from __future__ import annotations

import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    discogs_id: Mapped[int | None] = mapped_column(unique=True)
    spotify_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    image_url: Mapped[str | None] = mapped_column(String(1024))
    location: Mapped[str | None] = mapped_column(String(255))
    years_active: Mapped[str | None] = mapped_column(String(64))
    members: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(Text)
    bio_generated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    releases: Mapped[list["Release"]] = relationship(back_populates="artist", cascade="all, delete-orphan")
