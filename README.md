IN PROGRESS

# Music Explorer

A music discovery app that aggregates data from multiple sources to build rich artist and release pages, with AI-generated bios.

Search for an artist → choose from disambiguation results → browse their discography → dive into any album for the full tracklist, credits, and streaming links.

## How it works

When you visit an artist page for the first time the backend fans out across four APIs:

1. **Discogs** – artist profile text and metadata
2. **Spotify** – artist image and genre tags
3. **MusicBrainz** – full discography (albums, EPs, singles, compilations, mixtapes), years active, location, and band members; rate-limited to 1 req/s per their terms
4. **Genius** – fallback bio text when the Discogs profile is sparse

The aggregated facts are passed to **Claude Haiku** which writes a concise, grounded ~150-word bio in plain prose. The result is cached in PostgreSQL so subsequent visits are instant.

Release pages pull tracklists, personnel credits, cover art, and streaming links from MusicBrainz and the Cover Art Archive.

## Tech stack

| Layer | What |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy (async), asyncpg |
| Database | PostgreSQL 16 (Docker) |
| AI | Anthropic Claude Haiku (`claude-haiku-4-5`) |
| Frontend | React 18, Vite, React Router |
| External APIs | MusicBrainz, Discogs, Spotify, Genius |

## Getting started

### Prerequisites

- Python 3.13+
- Node 20+
- Docker (for Postgres)
- API keys for Discogs, Spotify (client credentials), and Anthropic

### 1. Start the database

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in your API keys in .env

uvicorn app.main:app --reload
```

The API will be at `http://localhost:8000`. On first start, SQLAlchemy creates the tables automatically.

### 3. Frontend

```bash
cd frontend
npm install

cp .env.example .env.local
# VITE_API_BASE_URL=http://localhost:8000

npm run dev
```

Open `http://localhost:5173`.

## Project structure

```
backend/
  app/
    models/         SQLAlchemy ORM models (Artist, Release)
    schemas/        Pydantic response schemas
    routers/        FastAPI route handlers
    services/
      bio.py        Claude Haiku bio generation
      musicbrainz.py  Throttled MusicBrainz client + release categorisation
      discogs.py    Discogs API client
      spotify.py    Spotify client-credentials flow + artist lookup
      genius.py     Genius bio scraping
      artist_cache.py  Orchestrates the multi-API fetch and DB cache
      release_detail.py  Assembles the release page payload
frontend/
  src/
    pages/          SearchPage, DisambiguationPage, ArtistPage, ReleasePage
    components/     VinylSpinner, ColorSpine
    api/client.js   Typed fetch wrappers
```

## Environment variables

**backend/.env**

| Variable | Description |
|---|---|
| `DATABASE_URL` | asyncpg connection string |
| `DISCOGS_TOKEN` | Discogs personal access token |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret |
| `ANTHROPIC_API_KEY` | Anthropic API key |

**frontend/.env.local**

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Backend base URL (default `http://localhost:8000`) |
