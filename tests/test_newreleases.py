import pytest
from unittest.mock import AsyncMock, MagicMock
from api.errors import Errors
from api.newreleases.newreleases import NewReleases

class FakeNewReleases(NewReleases):
    def __init__(self):
        self.errors = AsyncMock(spec=Errors)
        self.get_track_info = AsyncMock(return_value=[{"title": "Test Track"}])
        self.get_album_info = AsyncMock(return_value=[])
        self.aiohttp = AsyncMock()
        self.api_endpoints = MagicMock(new_releases_url="https://gaana.com/apiv2?page=0&type=miscNewRelease&language=")

@pytest.mark.asyncio
async def test_get_new_releases_returns_tracks_when_no_albums_found():
    formatter = FakeNewReleases()
    fake_response = AsyncMock()
    fake_response.json.return_value = {
        "entities": [
            {"entity_type": "TR", "seokey": "test-track"},
        ]
    }
    formatter.aiohttp.post.return_value = fake_response

    result = await formatter.get_new_releases("english", 1)

    formatter.errors.no_results.assert_not_called()
    assert result["tracks"] == [{"title": "Test Track"}]
    assert result["albums"] == []

@pytest.mark.asyncio
async def test_get_new_releases_returns_error_when_nothing_found():
    formatter = FakeNewReleases()
    fake_response = AsyncMock()
    fake_response.json.return_value = {"entities": []}
    formatter.aiohttp.post.return_value = fake_response

    await formatter.get_new_releases("english", 1)

    formatter.errors.no_results.assert_called_once()
