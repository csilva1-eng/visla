from fastapi import APIRouter, Request, Depends
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
import sys
from bot import InstaBot
from db.database import get_db
import httpx
import os
_current_sys_path = sys.path.copy()


try:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dependencies"))
    from dependencies import get_current_user
finally:    
    sys.path = _current_sys_path


router = APIRouter()

@router.post("/webhook")
async def receive_message( request: Request, db: AsyncSession = Depends(get_db)):
    print("sending message")
    body = await request.json()
    instagram_id = str(body.get("entry")[0]["messaging"][0]["sender"]["id"])
    val = await InstaBot.handle_message(body, instagram_id, db)

    await send_message(instagram_id, val)

    print("message sent")
    print("returned ok")
    return {"status": "ok"}

async def send_message(instagram_user_id: str, message: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"https://graph.facebook.com/v25.0/{os.getenv('PAGE_ID')}/messages",
            params = {"access_token": os.getenv("SHAX_PAGE_TOKEN")},
            json={
                "recipient": {"id": instagram_user_id},
                "message": {"text": message},
                "messaging_type": "RESPONSE",
            }
        )

    result = response.json()

    if "error" in result:
        print(f"Error sending DM: {result['error']}")
        return False
    return True

@router.get("/webhook")
async def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    InstaBot.handle_verify(hub_mode, hub_challenge, hub_verify_token)



