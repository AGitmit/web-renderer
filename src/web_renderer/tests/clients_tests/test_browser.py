import uuid
import pyppeteer.browser
import pytest
import pyppeteer
import unittest.mock as mocker

from web_renderer.clients.browser import CACHE, PageActionType


def test_browser_none(mock_browser):
    assert mock_browser.browser == None


@pytest.mark.asyncio
async def test_get_browser(mock_browser):
    assert mock_browser.browser == None
    await mock_browser.get_browser()
    assert isinstance(mock_browser.browser, pyppeteer.browser.Browser)
    assert mock_browser.browser != None


@pytest.mark.asyncio
async def test_get_new_page(mock_browser):
    async with mock_browser.get_new_page() as page:
        assert isinstance(page, pyppeteer.page.Page)
    assert isinstance(mock_browser.browser, pyppeteer.browser.Browser)


@pytest.mark.asyncio
async def test_close_browser(mock_browser):
    assert mock_browser.browser == None
    await mock_browser.get_browser()
    assert mock_browser.browser != None
    mock_browser.close_browser()
    assert mock_browser.browser == None


@pytest.mark.asyncio
async def test_start_page_session(mock_browser):
    session_id = uuid.uuid4()
    await mock_browser.start_page_session(session_id)
    assert session_id in CACHE
    assert CACHE[session_id] in await mock_browser.browser.pages()
    del CACHE[session_id]


@pytest.mark.asyncio
async def test_retrieve_cached_page(mock_browser):
    session_id = uuid.uuid4()
    await mock_browser.start_page_session(session_id)
    assert session_id in CACHE
    assert CACHE[session_id] in await mock_browser.browser.pages()
    page = await mock_browser.retrieve_cached_page(session_id)
    assert isinstance(page, pyppeteer.page.Page)
    del CACHE[session_id]


@pytest.mark.asyncio
async def test_remove_cached_page(mock_browser):
    session_id = uuid.uuid4()
    await mock_browser.start_page_session(session_id)
    assert session_id in CACHE
    assert CACHE[session_id] in await mock_browser.browser.pages()
    await mock_browser.remove_cached_page(session_id)
    assert session_id not in CACHE
    pages = list(await mock_browser.browser.pages())
    assert len(pages) == 1  # default len of the pages list


@pytest.mark.asyncio
async def test_extract_page_contents(mock_browser):
    async with mock_browser.get_new_page() as page:
        mocker.patch("page.title", return_value="test")
        mocker.patch("page.content", return_value="test")
        mocker.patch("page.cookies", return_value=[])
        mocker.patch("page.url", return_value="test")
        assert isinstance(await mock_browser.extract_page_contents(page), dict)


# @pytest.mark.asyncio
# async def test_fetch_page_contents(mock_browser):
#     page = mocker.MagicMock()
#     page.title = "test"
#     page.content = "test"
#     page.cookies = []
#     page.url = "test"
#     mocker.patch("pyppeteer.page.Page.goto", return_value=page)
#     assert isinstance(await mock_browser.fetch_page_contents("http://www.google.com", timeout=10), dict)


@pytest.mark.asyncio
async def test_fetch_page_contents_timeout(mock_browser):
    with pytest.raises(TimeoutError):
        assert await mock_browser.fetch_page_contents("https://www.google.com/timeout", timeout=1)


@pytest.mark.asyncio
async def test_page_action(mock_browser):
    async with mock_browser.get_new_page() as page:
        mocker.patch("page.title", return_value="test")
        mocker.patch(
            "page.content",
            return_value="""
                <html>
                    <body>
                        <div id="test" class="container">
                            <h1>Welcome to Fake Website</h1>
                            <p>This is some fake content for demonstration.</p>
                            <ul>
                                <li>Item 1</li>
                                <li>Item 2</li>
                                <li>Item 3</li>
                            </ul>
                        </div>
                    </body>
                </html>
            """,
        )
        mocker.patch("page.cookies", return_value=[])
        mocker.patch("page.url", return_value="test")
        mocker.patch("page.goto", return_value=page)
        await mock_browser.page_action(page, PageActionType.CLICK, selector="html")


@pytest.mark.asyncio
async def test_page_action_error(mock_browser):
    with pytest.raises(BaseException):
        async with mock_browser.get_new_page() as page:
            mocker.patch("page.title", return_value="test")
            mocker.patch("page.content", return_value="test")
            mocker.patch("page.cookies", return_value=[])
            mocker.patch("page.url", return_value="test")
            await mock_browser.page_action(page, PageActionType.CLICK)
