import uuid
import asyncio
import pyppeteer
from web_renderer.clients.renderer import HeadlessBrowserClient
from web_renderer.logger import logger
from web_renderer.schemas.constants.page_action_type import PageActionType
from web_renderer.config import config as conf


class WhatsAppClient:
    _is_authorized = False
    _msg_queue = []

    @classmethod
    async def authorize_whatsapp_web(cls):
        async with HeadlessBrowserClient.get_new_page(one_time_use=True, headless=False) as p:
            await p.goto(conf.whatsapp_web_url)
            input("Press any key after linking the device with WhatsApp web to continue...")
            cls._is_authorized = True

    @classmethod
    def add_new_msg_to_queue(cls, phone: str, content: str) -> bool:  # add phone validation
        try:
            cls._msg_queue.append((phone, content))
            return True
        except Exception as e:
            logger.error(e)
            return False

    @classmethod
    async def msg_manager(cls):
        while True:
            if cls._msg_queue:
                phone, content = cls._msg_queue.pop(0)
                await cls.send_msg(phone, content)
            await asyncio.sleep(1)

    @classmethod
    async def send_msg(cls, phone: str, content: str) -> bool:
        try:
            if cls._is_authorized:
                async with HeadlessBrowserClient.get_new_page(headless=True, autoClose=False) as p:
                    p.setDefaultNavigationTimeout(30000)  # Set to 30 seconds
                    await p.goto(
                        f"{conf.whatsapp_web_url}/send/?phone={phone}&text={content}&type=phone_number&app_absent=0"
                    )
                    await p.waitForSelector(
                        conf.whatsapp_web_send_button_selector, visible=True, timeout=10000
                    )
                    await p.keyboard.press("Enter")
                    await asyncio.sleep(3)
                logger.info(f"Message sent to {phone} successfully.")
                return True

            else:
                await cls.authorize_whatsapp_web()
                await cls.send_msg(phone, content)

        except pyppeteer.errors.TimeoutError as e:
            logger.error(
                f"Failed to send message to {phone}; {e} - please verify that your device is authroized in WhatsApp web."
            )
            cls._is_authorized = False

        except Exception as e:
            logger.error(f"Failed to send message to {phone}; {e}")
            return False
