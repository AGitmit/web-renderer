from fastapi import FastAPI

# relative imports
from web_renderer.api.routes.render import router as RenderRouter
from web_renderer.api.routes import router as IndexRouter
from web_renderer.api.routes.browser import router as BrowserRouter
from web_renderer.config import config as conf


app = FastAPI(
    title="Web-Renderer",
    version=conf.app_version,
    description="A Headless-browser HTTP API application powered by Pyppeteer",
)

for router in [
    IndexRouter,
    RenderRouter,
    BrowserRouter,
]:
    app.include_router(router)
