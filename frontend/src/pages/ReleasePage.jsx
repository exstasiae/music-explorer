import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getRelease } from "../api/client";
import ColorSpine from "../components/ColorSpine";
import VinylSpinner from "../components/VinylSpinner";

export default function ReleasePage() {
  const { mbid } = useParams();
  const navigate = useNavigate();
  const [release, setRelease] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    setStatus("loading");
    setRelease(null);
    getRelease(mbid)
      .then((data) => {
        setRelease(data);
        setStatus("done");
      })
      .catch(() => setStatus("error"));
  }, [mbid]);

  if (status === "loading") {
    return (
      <div className="release-page">
        <VinylSpinner />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="release-page">
        <p>Could not load this release.</p>
      </div>
    );
  }

  return (
    <div className="release-page">
      <ColorSpine imageUrl={release.cover_url} />
      <button className="breadcrumb breadcrumb-button" onClick={() => navigate(-1)}>
        ← Back
      </button>
      <div className="release-hero">
        <div
          className="release-hero-bg"
          style={{ backgroundImage: `url(${release.cover_url})` }}
        />
        <div className="release-hero-content">
          <span className="cover-with-vinyl">
            <img className="release-hero-cover" src={release.cover_url} alt={release.title} />
          </span>
          <div>
            <h2>{release.title}</h2>
            <dl className="artist-meta">
              <div>
                <dt>Type</dt>
                <dd>
                  <span className="stamp">{release.release_type}</span>
                </dd>
              </div>
              {release.release_date && (
                <div>
                  <dt>Released</dt>
                  <dd>{release.release_date}</dd>
                </div>
              )}
              {release.label && (
                <div>
                  <dt>Label</dt>
                  <dd>{release.label}</dd>
                </div>
              )}
              {release.genres.length > 0 && (
                <div>
                  <dt>Genres</dt>
                  <dd className="stamp-row">
                    {release.genres.map((genre) => (
                      <span className="stamp" key={genre}>
                        {genre}
                      </span>
                    ))}
                  </dd>
                </div>
              )}
            </dl>
            {release.links.length > 0 && (
              <div className="listen-links">
                {release.links.map((link) => (
                  <a
                    key={link.service}
                    href={link.url}
                    target="_blank"
                    rel="noreferrer"
                    className="listen-link"
                  >
                    {link.service}
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      {release.tracks.length > 0 && (
        <ol className="tracklist">
          {release.tracks.map((track, index) => (
            <li key={`${track.position}-${index}`}>
              <span className="track-position">{track.position}</span>
              <span className="track-title">
                {track.title}
                {track.features.length > 0 && (
                  <span className="track-features"> (feat. {track.features.join(", ")})</span>
                )}
              </span>
              <span className="track-leader" />
              {track.duration && <span className="track-duration">{track.duration}</span>}
            </li>
          ))}
          {release.total_duration && (
            <li className="tracklist-total">
              <span className="track-title">Total Length</span>
              <span className="track-leader" />
              <span className="track-duration">{release.total_duration}</span>
            </li>
          )}
        </ol>
      )}
      {release.personnel.length > 0 && (
        <section className="personnel">
          <h3>Personnel</h3>
          <dl className="personnel-list">
            {release.personnel.map((group) => (
              <div key={group.role}>
                <dt>{group.role}</dt>
                <dd>{group.names.join(", ")}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}
    </div>
  );
}
