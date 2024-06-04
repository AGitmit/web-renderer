import pytest
import jinja2


def test_renderer_jinjaEnv(mock_renderer):
    assert isinstance(mock_renderer.jinjaEnv, jinja2.Environment)


@pytest.mark.asyncio
async def test_file_to_png(mock_renderer, mocker):
    mocker.patch("pyppeteer.page.Page.goto", return_value=mocker.Mock())
    mocker.patch("pyppeteer.page.Page.screenshot", return_value=b"test")
    assert isinstance(await mock_renderer.file_to_png("test"), bytes)


# @pytest.mark.asyncio
# async def test_file_to_png_error(mock_renderer):
#     with pytest.raises(FileNotFoundError):
#         assert await mock_renderer.file_to_png("test")
