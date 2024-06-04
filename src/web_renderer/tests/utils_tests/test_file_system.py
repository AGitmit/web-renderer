import pytest

from web_renderer.utils.file_system import save_file, validate_output_location


@pytest.mark.asyncio
async def test_validate_output_location(tmp_path):
    assert await validate_output_location(tmp_path.__str__())


@pytest.mark.asyncio
async def test_save_file(tmp_path):
    assert await save_file(tmp_path.__str__(), "test", "test", "txt")
