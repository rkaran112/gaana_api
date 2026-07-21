import pytest
from unittest.mock import AsyncMock, MagicMock
from api.functions import Functions
from api.errors import Errors
from api.artists.artists import Artists

class FakeFormatter(Artists):
    def __init__(self):
        self.functions = AsyncMock(spec=Functions)
        self.errors = AsyncMock(spec=Errors)
        self.info = False ## Don't get artist tracks

class FakeSimilarArtists(Artists):
    def __init__(self, entities):
        self.aiohttp = MagicMock()
        self.aiohttp.get = AsyncMock(return_value=MagicMock(json=AsyncMock(return_value={"entities": entities})))
        self.api_endpoints = MagicMock(similar_artists_url="https://example.com/similar-artists/")
        self.errors = Errors()

    async def format_json_similar_artists(self, results: dict) -> dict:
        return {"seokey": results["seokey"]}

class FakeTopTracks(Artists):
    def __init__(self, entities):
        self.aiohttp = MagicMock()
        self.aiohttp.post = AsyncMock(return_value=MagicMock(json=AsyncMock(return_value={"entities": entities})))
        self.api_endpoints = MagicMock(artist_top_tracks="https://example.com/artist-top-tracks/")
        self.errors = Errors()

    async def get_track_info(self, track_id: list) -> list:
        return [{"seokey": seokey} for seokey in track_id]

class FakeSearchArtists(Artists):
    def __init__(self, artists):
        self.aiohttp = MagicMock()
        self.aiohttp.post = AsyncMock(return_value=MagicMock(json=AsyncMock(return_value={"gr": [{"gd": artists}]})))
        self.api_endpoints = MagicMock(search_artists_url="https://example.com/search-artists/")
        self.errors = Errors()

    async def get_artist_info(self, artist_id: list, info: bool) -> list:
        return [{"seokey": seokey} for seokey in artist_id]


@pytest.mark.asyncio
async def test_format_json_artists():
    formatter = FakeFormatter()

    gaana_input = {
        "artist": [
            {
                "seokey": "artist-seokey-123",
                "artist_id": "artist-id-456",
                "name": "Test Artist",
                "songs": 42,
                "albums": 5,
                "favorite_count": 1000,
                "atw": "https://cdn.gaana.com/images/artist/size_m/artist123.jpg"
            }
        ]
    }

    result = await formatter.format_json_artists(gaana_input)

    assert result["seokey"] == "artist-seokey-123"
    assert result["images"]["urls"]["large_artwork"] == "https://cdn.gaana.com/images/artist/size_l/artist123.jpg"
    assert "artist_id" in result
    assert "artist_url" in result
    assert "top_tracks" not in result ## Didn't request tracks
    
@pytest.mark.asyncio
async def test_format_json_similar_artists():
    formatter = FakeFormatter()

    gaana_input = {
        "seokey": "artist-seokey-789",
        "entity_id": "artist-id-321",
        "name": "Mock Artist",
        "entity_info": [
            {"value": 7},   # album_count
            {"value": 42}   # song_count
        ],
        "favorite_count": 555,
        "atw": "https://cdn.gaana.com/images/artist/size_m/artist789.jpg"
    }

    result = await formatter.format_json_similar_artists(gaana_input)

    assert result["seokey"] == "artist-seokey-789"
    assert result["images"]["urls"]["large_artwork"] == "https://cdn.gaana.com/images/artist/size_l/artist789.jpg"
    assert "artist_id" in result
    assert "artist_url" in result

@pytest.mark.asyncio
async def test_get_similar_artists_limit_exceeds_available_entities():
    artists = FakeSimilarArtists([{"seokey": "artist-1"}, {"seokey": "artist-2"}])

    result = await artists.get_similar_artists("artist-id-123", 10)

    assert result == [{"seokey": "artist-1"}, {"seokey": "artist-2"}]

@pytest.mark.asyncio
async def test_get_similar_artists_no_entities_returns_error():
    artists = FakeSimilarArtists([])

    result = await artists.get_similar_artists("artist-id-123", 10)

    assert result == {"ERROR": "Unable to find any results!"}

@pytest.mark.asyncio
async def test_get_top_tracks_returns_track_data():
    artists = FakeTopTracks([{"seokey": "track-1"}, {"seokey": "track-2"}])

    result = await artists.get_top_tracks("artist-id-123")

    assert result == [{"seokey": "track-1"}, {"seokey": "track-2"}]

@pytest.mark.asyncio
async def test_get_top_tracks_missing_entities_returns_error():
    artists = FakeTopTracks(None)

    result = await artists.get_top_tracks("artist-id-123")

    assert result == {"ERROR": "Unable to find any results!"}

@pytest.mark.asyncio
async def test_search_artists_returns_artist_info():
    artists = FakeSearchArtists([{"seo": "artist-1"}, {"seo": "artist-2"}])

    result = await artists.search_artists("test query", 2)

    assert result == [{"seokey": "artist-1"}, {"seokey": "artist-2"}]

@pytest.mark.asyncio
async def test_search_artists_limit_exceeds_available_entities():
    artists = FakeSearchArtists([{"seo": "artist-1"}])

    result = await artists.search_artists("test query", 5)

    assert result == [{"seokey": "artist-1"}]

@pytest.mark.asyncio
async def test_search_artists_no_results_returns_error():
    artists = FakeSearchArtists([])

    result = await artists.search_artists("test query", 5)

    assert result == {"ERROR": "Unable to find any results!"}