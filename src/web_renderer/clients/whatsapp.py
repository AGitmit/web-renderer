import uuid
import asyncio
import pyppeteer
from web_renderer.clients.renderer import HeadlessBrowserClient
from web_renderer.logger import logger
from web_renderer.schemas.constants.page_action_type import PageActionType

class WhatsAppClient:
    _session_id = uuid.uuid4()
    _whatsapp_web: pyppeteer.page.Page = None
    _msg_queue = []

    @classmethod
    async def get_whatsapp_web(cls):
        if cls._whatsapp_web is None:
            await HeadlessBrowserClient.start_page_session(cls._session_id)
            cls._whatsapp_web = await HeadlessBrowserClient.retrieve_cached_page(cls._session_id)
            await HeadlessBrowserClient.page_action(cls._whatsapp_web, PageActionType.GOTO, url=f"https://web.whatsapp.com")
        return cls._whatsapp_web
    
    @classmethod
    def add_new_msg_to_queue(cls, phone: str, content: str, wait_time: int = 2) -> bool: # add phone validation
        try:
            cls._msg_queue.append((phone, content, wait_time))
            return True
        except Exception as e:
            logger.error(e)
            return False
    
    @classmethod
    async def msg_manager(cls):
        while True:
            if cls._msg_queue:
                phone, content, wait_time = cls._msg_queue.pop(0)
                await cls.send_msg(phone, content, wait_time)
            await asyncio.sleep(1)

    @classmethod
    async def send_msg(cls, phone: str, content: str, wait_time: int) -> bool:
        try:
            await HeadlessBrowserClient.page_action(await cls.get_whatsapp_web(), PageActionType.GOTO, url=f"https://web.whatsapp.com/send?phone={phone}&text={content}")
            await asyncio.sleep(10)
            await HeadlessBrowserClient.page_action(await cls.get_whatsapp_web(),PageActionType.CLICK, selector="#main > footer > div.x1n2onr6.xhtitgo.x9f619.x78zum5.x1q0g3np.xuk3077.x193iq5w.x122xwht.x1bmpntp.xs9asl8.x1swvt13.x1pi30zi.xnpuxes.copyable-area > div > span > div > div._ak1r > div.x123j3cw.xs9asl8.x9f619.x78zum5.x6s0dn4.xl56j7k.x1ofbdpd.x100vrsf.x1fns5xo > button")
            logger.info(f"Message sent to {phone} successfully.")
        except Exception as e:
            logger.error(f"Failed to send message to {phone}; {e}")
            return False
        return True