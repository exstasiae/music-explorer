const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function apiGet(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request to ${path} failed: ${response.status}`);
  }
  return response.json();
}

export async function searchArtists(query) {
  return apiGet(`/search?q=${encodeURIComponent(query)}`);
}

export async function getArtist(slug) {
  return apiGet(`/artists/${encodeURIComponent(slug)}`);
}

export async function getRelease(mbid) {
  return apiGet(`/releases/${encodeURIComponent(mbid)}`);
}
