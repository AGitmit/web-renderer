import uuid
import asyncio

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from web_renderer.config import config as conf
from web_renderer.logger import logger
from web_renderer.clients.whatsapp import WhatsAppClient
from web_renderer.schemas.requests import WhatsAppRequest


router = APIRouter(prefix=f"{conf.v1_url_prefix}/whatsapp", tags=["WhatsApp interactions"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def send_whatsapp_msg(args: WhatsAppRequest):
    try:
        WhatsAppClient.add_new_msg_to_queue(**args.dict())
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status": "success"})
    
    except asyncio.TimeoutError as e:
        msg = "Request has been timed-out!"
        logger.error(msg)
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=msg)

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))