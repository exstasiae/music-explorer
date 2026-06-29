import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { searchArtists } from "../api/client";
import VinylSpinner from "../components/VinylSpinner";

export default function DisambiguationPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("idle");

  useEffect(() => {
    if (!query) {
      setResults([]);
      setStatus("idle");
      return;
    }
    setStatus("loading");
    searchArtists(query)
      .then((data) => {
        setResults(data);
        setStatus("done");
      })
      .catch(() => setStatus("error"));
  }, [query]);

  return (
    <div className="disambiguation-page">
      <Link className="breadcrumb" to="/">
        ← Music Explorer
      </Link>
      <h2>Results for &ldquo;{query}&rdquo;</h2>
      {status === "loading" && <VinylSpinner />}
      {status === "error" && <p>Something went wrong. Please try again.</p>}
      {status === "done" && results.length === 0 && <p>No artists found.</p>}
      {status === "done" && (
        <ul className="artist-results">
          {results.map((artist) => (
            <li key={artist.slug}>
              <Link to={`/artist/${artist.slug}`}>
                {artist.thumb && <img src={artist.thumb} alt="" />}
                <span>{artist.name}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
