import uuid
import pydantic as pyd
import re

from web_renderer.schemas import sanitize_str
from web_renderer.schemas.constants.page_action_type import PageActionType

# browser
class FetchRequest(pyd.BaseModel):
    transaction_id: uuid.UUID
    url: str

    @pyd.validator("url")
    def sanitize_str(cls, value: str):
        if re.search(sanitize_str, value):
            raise ValueError(
                f"Illegal characters found in '{value}' - allowed special characters are '-' or '_'"
            )
        return value


class PageActionRequest(pyd.BaseModel):
    action: PageActionType
    selector: str | None = pyd.Field(default=None)
    options: dict | None = pyd.Field(default=None)
    credentials: dict | None = pyd.Field(default=None)
    user_agent: str | None = pyd.Field(default=None)
    url: str | None = pyd.Field(default=None)

    @pyd.validator("url")
    def sanitize_str(cls, value: str):
        if re.search(sanitize_str, value):
            raise ValueError(
                f"Illegal characters found in '{value}' - allowed special characters are '-' or '_'"
            )
        return value

class WhatsAppRequest(pyd.BaseModel):
    phone: str
    content: str
    wait_time: int = pyd.Field(default=2)