import uuid

from pydantic import BaseModel
from typing import Annotated

# relative imports
from web_renderer.schemas.constants.part_name import PartName


class Base64OfImageResponse(BaseModel):
    transaction_id: uuid.UUID
    image_type: PartName
    base64: Annotated[str, "base64 of an image"]


class PageContentResponse(BaseModel):
    url: str
    title: str | None
    content: str | None
    cookies: list | None
