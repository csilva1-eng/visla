from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from bot import InstaBot
from dependencies import get_current_user


router = APIRouter()

@router.post("/webhook")
async def receive_message(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    await InstaBot.handle_message(body, db)
    return {"status": "ok"}

@router.get("/webhook")
async def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    InstaBot.handle_verify(hub_mode, hub_challenge, hub_verify_token)



