import asyncio

from fastapi import FastAPI
# relative imports
from web_renderer.api.routes import router as IndexRouter
from web_renderer.api.routes.browser import router as BrowserRouter
from web_renderer.api.routes.whatsapp import router as WhatsAppRouter, WhatsAppClient
from web_renderer.config import config as conf

app = FastAPI(
    title="Web-Renderer",
    version=conf.app_version,
    description="A Headless-browser HTTP API application powered by Pyppeteer",
)

for router in [
    IndexRouter,
    BrowserRouter,
    WhatsAppRouter,
]:
    app.include_router(router)

@app.on_event("startup")
async def whatsapp_msg_manager():
    asyncio.create_task(WhatsAppClient.get_whatsapp_web())
    asyncio.create_task(WhatsAppClient.msg_manager())