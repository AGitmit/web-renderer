import pytest

from fastapi.testclient import TestClient
from web_renderer.logger import log_context
from pytest_httpx import HTTPXMock


log_context.set("Pytest")


@pytest.fixture(scope="session")
def mock_client():
    from web_renderer.api.app import app

    test_client = TestClient(app)
    return test_client


@pytest.fixture(scope="session")
def httpx_mock():
    return HTTPXMock()


@pytest.fixture(scope="function")
def mock_browser():
    from web_renderer.clients.browser import HeadlessBrowserClient

    browser = HeadlessBrowserClient()
    yield browser
    browser.close_browser()


@pytest.fixture(scope="module")
def mock_renderer():
    from web_renderer.clients.renderer import RendererClient

    renderer = RendererClient()
    return renderer
