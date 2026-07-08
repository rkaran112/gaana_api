import pytest
from api.gaanapy import GaanaPy

@pytest.mark.asyncio
async def test_gaanapy_is_awaitable():
    gaanapy = await GaanaPy()
    assert isinstance(gaanapy, GaanaPy)
    await gaanapy.aiohttp.close()
