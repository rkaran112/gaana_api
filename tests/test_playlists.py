import pytest
from unittest.mock import AsyncMock, MagicMock
from api.errors import Errors
from api.playlists.playlists import Playlists

class FakePlaylists(Playlists):
    def __init__(self):
        self.get_track_info = AsyncMock(return_value=[{"title": "Test Track"}])
        self.aiohttp = AsyncMock()
        self.api_endpoints = MagicMock(playlist_details_url="https://gaana.com/apiv2?type=playlistDetail&seokey=")
        self.errors = AsyncMock(spec=Errors)

@pytest.mark.asyncio
async def test_get_playlist_info_returns_track_data():
    formatter = FakePlaylists()
    fake_response = AsyncMock()
    fake_response.json.return_value = {
        "count": 2,
        "tracks": [
            {"seokey": "track-one"},
            {"seokey": "track-two"},
        ],
    }
    formatter.aiohttp.post.return_value = fake_response

    result = await formatter.get_playlist_info("test-playlist")

    formatter.aiohttp.post.assert_called_once_with(
        formatter.api_endpoints.playlist_details_url + "test-playlist"
    )
    formatter.get_track_info.assert_called_once_with(["track-one", "track-two"])
    assert result == [{"title": "Test Track"}]

@pytest.mark.asyncio
async def test_get_playlist_info_skips_missing_seokeys():
    formatter = FakePlaylists()
    fake_response = AsyncMock()
    fake_response.json.return_value = {
        "count": 3,
        "tracks": [
            {"seokey": "track-one"},
            {},
        ],
    }
    formatter.aiohttp.post.return_value = fake_response

    await formatter.get_playlist_info("test-playlist")

    formatter.get_track_info.assert_called_once_with(["track-one"])

@pytest.mark.asyncio
async def test_get_playlist_info_returns_no_results_for_invalid_playlist():
    formatter = FakePlaylists()
    formatter.errors = Errors()
    fake_response = AsyncMock()
    fake_response.json.return_value = {"ERROR": "Invalid Seokey!"}
    formatter.aiohttp.post.return_value = fake_response

    result = await formatter.get_playlist_info("bad-playlist")

    assert result == {"ERROR": "Unable to find any results!"}
    formatter.get_track_info.assert_not_called()

@pytest.mark.asyncio
async def test_get_playlist_info_returns_no_results_for_empty_playlist():
    formatter = FakePlaylists()
    formatter.errors = Errors()
    fake_response = AsyncMock()
    fake_response.json.return_value = {"count": 0, "tracks": []}
    formatter.aiohttp.post.return_value = fake_response

    result = await formatter.get_playlist_info("empty-playlist")

    assert result == {"ERROR": "Unable to find any results!"}
    formatter.get_track_info.assert_not_called()
