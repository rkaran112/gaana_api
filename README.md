# gaana_api

An unofficial JSON API for [Gaana](https://gaana.com), an Indian music streaming service, built with FastAPI. This repository is based on [ZingyTomato/GaanaPy](https://github.com/ZingyTomato/GaanaPy), with an added HTML demo player for quickly trying out search and playback.

## What it does

The API wraps Gaana's internal `apiv2` endpoints and exposes them as clean, structured JSON via FastAPI routes (see `api/endpoints.py` and `app.py`):

- `GET /songs/search` – search for tracks by name (`query`, optional `limit`)
- `GET /songs/info` – full track details by `seokey`, including decrypted HLS stream URLs at multiple bitrates
- `GET /albums/search` – search for albums (`query`, optional `limit`)
- `GET /albums/info` – album details by `seokey`
- `GET /artists/search` – search for artists (`query`, optional `limit`)
- `GET /artists/info` – artist details by `seokey`
- `GET /artists/similar` – similar artists by `artist_id`
- `GET /playlists/info` – playlist details by `seokey`
- `GET /trending` – trending tracks by `language`
- `GET /newreleases` – newly released songs/albums by `language`
- `GET /charts` – curated top-chart playlists
- `GET /demo/player` – a static HTML demo page (`demo-player.html`) for searching and playing tracks in the browser
- `GET /docs` – auto-generated FastAPI/Swagger docs

The core logic lives in `api/gaanapy.py` (orchestrates requests to Gaana), `api/functions.py` (helper utilities, including AES-CBC decryption of stream URLs via `pycryptodome`), and `api/errors.py` (shared error responses). Each resource (albums, artists, charts, new releases, playlists, songs, trending) has its own module under `api/`.

## Tech stack

- Python 3, [FastAPI](https://fastapi.tiangolo.com/) + [uvicorn](https://www.uvicorn.org/) for the web server
- [aiohttp](https://docs.aiohttp.org/) for async HTTP calls to Gaana's backend
- [pycryptodome](https://pycryptodome.readthedocs.io/) for decrypting stream URLs (AES-CBC)
- [pytest](https://docs.pytest.org/) + `pytest-asyncio` for the test suite (see `tests/`)
- Docker (a `Dockerfile` is included; `docker-compose.yml` as shipped points at the upstream `zingytomato/gaanapy:main` image rather than building locally)

See `requirements.txt` for exact pinned versions.

## Setup

```sh
git clone https://github.com/rkaran112/gaana_api
cd gaana_api
pip3 install -r requirements.txt
python3 -m uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000` (or `http://127.0.0.1:8000/docs` for interactive API docs, and `http://127.0.0.1:8000/demo/player` for the demo player UI).

### Docker (build locally)

```sh
docker build -t gaana_api .
docker run -p 8000:8000 gaana_api
```

Note: the included `docker-compose.yml` pulls the upstream `zingytomato/gaanapy:main` image rather than building from this repo's `Dockerfile`. Edit it (or use `docker build`/`docker run` above) if you want to run the code in this repo specifically.

## Usage example

Search for a song:

```sh
curl "http://127.0.0.1:8000/songs/search?query=tyler%20herro&limit=5"
```

Returns a JSON array of matching tracks, each including metadata (title, artists, album, genre, release date) plus decrypted `stream_urls` at multiple qualities and `images` at multiple sizes.

Get details for a specific track by its `seokey` (the slug from a `gaana.com/song/<seokey>` URL):

```sh
curl "http://127.0.0.1:8000/songs/info?seokey=tyler-herro"
```

## Status

Functionally complete for its scope: all documented endpoints are implemented with real logic (no stub functions or `TODO`/`FIXME` markers found), error cases (invalid seokey, no results) are handled via `api/errors.py`, and there's a test suite (`tests/`) covering the helper functions and each resource module. A couple of things worth knowing if you extend this:

- The AES decryption key in `api/functions.py` is hardcoded and commented as something Gaana "can possibly keep changing" — if stream URL decryption starts failing, that key is the first place to check.
- Two endpoints (`similar_songs_url`, `similar_albums_url` in `api/endpoints.py`) are commented out, noted as currently returning nothing from Gaana's side.
- `docker-compose.yml` references the upstream image rather than this repo's own `Dockerfile` (see Docker section above).

This is an unofficial, reverse-engineered client against Gaana's private API, so it may break if Gaana changes their backend.
