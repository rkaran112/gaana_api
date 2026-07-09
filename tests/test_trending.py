import pytest
from unittest.mock import AsyncMock, MagicMock
from api.errors import Errors
from api.trending.trending import Trending

class FakeTrending(Trending):
    def __init__(self):
        self.errors = AsyncMock(spec=Errors)
        self.get_track_info = AsyncMock(return_value=[{"title": "Test Track"}])
        self.aiohttp = AsyncMock()
        self.api_endpoints = MagicMock(trending_url="https://gaana.com/apiv2?type=miscTrendingSongs")

@pytest.mark.asyncio
async def test_get_trending_returns_tracks():
    formatter = FakeTrending()
    fake_response = AsyncMock()
    fake_response.json.return_value = {
        "entities": [
            {"seokey": "test-track"},
        ]
    }
    formatter.aiohttp.post.return_value = fake_response

    result = await formatter.get_trending("english", 1)

    formatter.errors.no_results.assert_not_called()
    formatter.get_track_info.assert_called_once_with(["test-track"])
    assert result == [{"title": "Test Track"}]

@pytest.mark.asyncio
async def test_get_trending_returns_error_when_nothing_found():
    formatter = FakeTrending()
    fake_response = AsyncMock()
    fake_response.json.return_value = {"entities": []}
    formatter.aiohttp.post.return_value = fake_response

    await formatter.get_trending("english", 5)

    formatter.errors.no_results.assert_called_once()
    formatter.get_track_info.assert_not_called()
