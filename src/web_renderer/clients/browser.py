import pyppeteer
import atexit
import asyncio
import cachetools
import uuid
import pydantic as pyd

from contextlib import asynccontextmanager

import pyppeteer.chromium_downloader
import pyppeteer.page
from web_renderer.config import config as conf
from web_renderer.logger import log_execution_metrics, logger
from web_renderer.schemas.constants.page_action_type import PageActionType


CACHE = cachetools.TTLCache(maxsize=conf.max_cached, ttl=conf.cache_ttl)


class HeadlessBrowserClient:
    browser = None

    @classmethod
    async def get_browser(cls, **kwargs):
        "Get the browser's instance; created a new browser if none in already running"
        try:
            if cls.browser is None:
                # if not pyppeteer.chromium_downloader.check_chromium():
                #     pyppeteer.chromium_downloader.download_chromium()

                config = dict(
                    headless=kwargs.get("headless", True),
                    autoClose=kwargs.get("autoClose", False),
                    args=[
                        "--disable-web-security",
                        "--host-resolver-rules=MAP localhost 127.0.0.1",
                        "--disable-gpu",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                    executablePath=conf.browser_path,
                    userDataDir=conf.user_data_dir_path,
                )
                cls.browser = await pyppeteer.launch(**config)
                atexit.register(cls.close_browser)
            return cls.browser
        except Exception as e:
            logger.error(e)
            raise

    @classmethod
    @asynccontextmanager
    async def get_new_page(cls, one_time_use: bool = False, **kwargs):
        browser = await cls.get_browser(**kwargs)
        new_page = await browser.newPage()
        try:
            yield new_page
        except Exception as e:
            logger.error(f"Page exception: {e}")
        finally:
            await new_page.close()
            if one_time_use:
                await cls.browser.close()
                cls.browser = None

    @classmethod
    def close_browser(cls) -> None:
        if cls.browser is not None:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(cls.browser.close)
            cls.browser = None

    @classmethod
    async def start_page_session(cls, session_id: uuid.UUID) -> None:
        "Created a new pages and storing it in cache coupled with it's session ID"
        if CACHE.get(session_id):
            raise Exception("Page session already exists for this session_id.")
        browser = await cls.get_browser()
        new_page = await browser.newPage()
        CACHE[session_id] = new_page

    @classmethod
    async def retrieve_cached_page(cls, session_id: uuid.UUID) -> pyppeteer.page.Page:
        "Retrieves a page from cache memory"
        page: pyppeteer.page.Page = CACHE.get(session_id)
        if not page:
            raise KeyError(
                f"Page not found [page: '{session_id}'] - session has already been closed"
            )
        return page

    @classmethod
    async def remove_cached_page(cls, session_id: uuid.UUID) -> None:
        "Removes a cached page from memory - ending the session"
        page = await cls.retrieve_cached_page(session_id)
        try:
            await page.close()
        except Exception as e:
            raise
        finally:
            del CACHE[session_id]

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def extract_page_contents(cls, page: pyppeteer.page.Page) -> dict:
        return dict(
            url=page.url,
            title=await page.title(),
            content=await page.content(),
            cookies=await page.cookies(),
        )

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def fetch_page_contents(cls, url: str, **kwargs) -> dict:
        async with HeadlessBrowserClient.get_new_page() as page:
            logger.debug(f"Browser fetching URL='{url}'...")
            fetch_config = {
                "waitUntil": kwargs.pop("waitUntil", "domcontentloaded"),
                "timeout": kwargs.pop("timeout", 0),
            }
            fetch_config.update(**kwargs)
            await page.goto(url, options=fetch_config)
            logger.debug(f"Page loaded: URL='{url}'")
            return await cls.extract_page_contents(page)

    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def page_action(cls, page: pyppeteer.page.Page, action: PageActionType, **kwargs) -> dict:
        try:
            match action:
                case PageActionType.CLICK:
                    selector = kwargs.pop("selector")
                    options = kwargs.pop("options", None)
                    await page.waitForSelector(selector)
                    await page.click(selector, options)
                case PageActionType.AUTHENTICATE:
                    credentials = kwargs.pop("credentials")
                    await page.authenticate(credentials)
                case PageActionType.SET_USER_AGENT:
                    user_agent = kwargs.pop("user_agent")
                    await page.setUserAgent(user_agent)
                case PageActionType.SCREENSHOT:
                    options = kwargs.pop("options", None)
                    await page.screenshot(options)
                case PageActionType.GOTO:
                    url = kwargs.pop("url")
                    options = kwargs.pop("options", None)
                    await page.goto(url, options)
                case PageActionType.GO_BACK:
                    options = kwargs.pop("options", None)
                    await page.goBack(options)
                case PageActionType.GO_FORWARD:
                    options = kwargs.pop("options", None)
                    await page.goForward(options)
                case PageActionType.ENTER:
                    await page.keyboard.press("Enter")

            return await cls.extract_page_contents(page)

        except Exception as e:
            logger.error(e)
            raise
