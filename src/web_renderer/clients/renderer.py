import pydantic as pyd

from web_renderer.logger import log_execution_metrics
from web_renderer.clients.browser import HeadlessBrowserClient


class RendererClient:
    @classmethod
    @pyd.validate_arguments
    @log_execution_metrics
    async def file_to_png(
        cls, file_path: str, width: int = 1200, height: int = 800, **kwargs
    ) -> str:
        "Opening a new browser page, navigating to the given path and rendering it as a PNG."
        file_url = "file://" + file_path
        async with HeadlessBrowserClient.get_new_page() as page:
            await page.setViewport({"width": width, "height": height})
            await page.goto(file_url, options=kwargs)
            png_image = await page.screenshot()
        return png_image

    @classmethod
    @pyd.validate_arguments
    async def file_to_pdf(cls, file_path: str) -> str:
        "Opening a new browser page, navigating to the given path and rendering it as a PDF."
        async with HeadlessBrowserClient.get_new_page() as page:
            await page.goto(f"file://{file_path}", {"waitUntil": "domcontentloaded"})
            pdf_content = await page.pdf()
        return pdf_content
