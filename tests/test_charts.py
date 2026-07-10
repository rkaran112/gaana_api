import pytest
from unittest.mock import AsyncMock, MagicMock
from api.functions import Functions
from api.errors import Errors
from api.charts.charts import Charts

class FakeFormatter(Charts):
    def __init__(self):
        self.functions = AsyncMock(spec=Functions)

class FakeCharts(Charts):
    def __init__(self, entities):
        self.aiohttp = MagicMock()
        self.aiohttp.post = AsyncMock(return_value=MagicMock(json=AsyncMock(return_value={"entities": entities})))
        self.api_endpoints = MagicMock(charts_url="https://example.com/charts/")
        self.errors = Errors()

    async def format_json_charts(self, results: dict) -> dict:
        return {"seokey": results["seokey"]}

@pytest.mark.asyncio
async def test_format_json_charts():
    formatter = FakeFormatter()
    
    formatter.functions.isExplicit.return_value = True

    gaana_input = {
        "seokey": "test-playlist-123",
        "entity_id": "playlist-456",
        "name": "Test Playlist",
        "language": "English",
        "favorite_count": 789,
        "entity_info": [
            {}, {}, {}, {}, {}, {}, {"value": 1},  # index 6 = is_explicit
            {}, {}, {}, {}, {}, {"value": 99999}   # last = play_count
        ],
        "atw": "https://cdn.gaana.com/images/playlist/size_m.jpg"
    }


    result = await formatter.format_json_charts(gaana_input)

    assert result["seokey"] == "test-playlist-123"
    assert result["images"]["urls"]["large_artwork"] == "https://cdn.gaana.com/images/playlist/size_l.jpg"
    assert "playlist_id" in result
    assert "playlist_url" in result

@pytest.mark.asyncio
async def test_get_charts_limit_exceeds_available_entities():
    charts = FakeCharts([{"seokey": "chart-1"}, {"seokey": "chart-2"}])

    result = await charts.get_charts(10)

    assert result == [{"seokey": "chart-1"}, {"seokey": "chart-2"}]

@pytest.mark.asyncio
async def test_get_charts_no_entities_returns_error():
    charts = FakeCharts([])

    result = await charts.get_charts(10)

    assert result == {"ERROR": "Unable to find any results!"}