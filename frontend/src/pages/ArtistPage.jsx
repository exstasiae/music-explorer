import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getArtist } from "../api/client";
import VinylSpinner from "../components/VinylSpinner";

const CATEGORY_ORDER = ["Album", "Mixtape", "EP", "Compilation", "Single"];
const LINKABLE_CATEGORIES = new Set(["Album", "Mixtape", "EP"]);

export default function ArtistPage() {
  const { artistSlug } = useParams();
  const [artist, setArtist] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    setStatus("loading");
    setArtist(null);
    getArtist(artistSlug)
      .then((data) => {
        setArtist(data);
        setStatus("done");
      })
      .catch(() => setStatus("error"));
  }, [artistSlug]);

  if (status === "loading") {
    return (
      <div className="artist-page">
        <VinylSpinner />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="artist-page">
        <p>Could not load this artist.</p>
      </div>
    );
  }

  return (
    <div className="artist-page">
      <Link className="breadcrumb" to="/">
        ← Music Explorer
      </Link>
      <div className="artist-hero">
        {artist.image_url && (
          <div
            className="artist-hero-bg"
            style={{ backgroundImage: `url(${artist.image_url})` }}
          />
        )}
        <div className="artist-hero-content">
          {artist.image_url && (
            <span className="cover-with-vinyl">
              <img className="artist-avatar" src={artist.image_url} alt={artist.name} />
            </span>
          )}
          <div>
            <h2>{artist.name}</h2>
            <dl className="artist-meta">
              {artist.genres.length > 0 && (
                <div>
                  <dt>Genres</dt>
                  <dd className="stamp-row">
                    {artist.genres.map((genre) => (
                      <span className="stamp" key={genre}>
                        {genre}
                      </span>
                    ))}
                  </dd>
                </div>
              )}
              {artist.years_active && (
                <div>
                  <dt>Years active</dt>
                  <dd>{artist.years_active}</dd>
                </div>
              )}
              {artist.location && (
                <div>
                  <dt>Based in</dt>
                  <dd>{artist.location}</dd>
                </div>
              )}
              {artist.members.length > 0 && (
                <div>
                  <dt>Members</dt>
                  <dd>{artist.members.join(", ")}</dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>
      {artist.bio && <p className="artist-bio">{artist.bio}</p>}
      {CATEGORY_ORDER.map((category) => {
        const releases = artist.releases[category] || [];
        if (releases.length === 0) return null;
        return (
          <section key={category}>
            <h3>{category}</h3>
            <div className="release-grid">
              {releases.map((release) => {
                const cover = (
                  <div className="release-cover">
                    {release.musicbrainz_id && (
                      <img
                        src={`https://coverartarchive.org/release-group/${release.musicbrainz_id}/front-250`}
                        alt=""
                        loading="lazy"
                        onError={(event) => {
                          event.target.style.visibility = "hidden";
                        }}
                      />
                    )}
                  </div>
                );
                const title = (
                  <p className="release-title">
                    {release.title}
                    {release.year ? ` (${release.year})` : ""}
                  </p>
                );
                const key = `${release.musicbrainz_id}-${release.title}`;
                if (LINKABLE_CATEGORIES.has(category) && release.musicbrainz_id) {
                  return (
                    <Link
                      className="release-card"
                      key={key}
                      to={`/release/${release.musicbrainz_id}`}
                    >
                      {cover}
                      {title}
                    </Link>
                  );
                }
                return (
                  <div className="release-card" key={key}>
                    {cover}
                    {title}
                  </div>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
