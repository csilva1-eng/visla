from fastapi import APIRouter, Request, Depends, Query
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
import sys
from bot import InstaBot
from db.database import get_db
import httpx
import os
from navigator import client
import json
from bot.calendar import create_event, list_events
from sqlalchemy import select
from db.models import User
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
    try:

        body = await request.json()
        
        entry = body.get("entry", [])
        if not entry:
            return None

        messaging = body.get('entry')[0]['messaging'][0]

        if "read" in messaging:
            return None
        if "delivery" in messaging:
            return None

        if "message" not in messaging:
            return None
        if messaging["message"].get("is_echo"):
            return None

        instagram_id = str(body.get("entry")[0]["messaging"][0]["sender"]["id"])

        result = await db.execute(select(User).where(User.instagram_id == instagram_id))
        user = result.scalar_one_or_none()

        if not user:
            send_message(instagram_id, f"Welcome to Visla, to get started click {generate_onboarding_link(instagram_id)}")
            return {"status": "ok"}

        val = await InstaBot.handle_message(body, db)
        
        if val and isinstance(val,dict) and val.get('message'):
            if val.get('caption'):
                postEvent = json.loads(await get_event_details(val.get('caption')))
                if postEvent:
                    events = await list_events(user.google_refresh_token)

                    for event in events:
                        if event["start"]["dateTime"] == val.get('date'):
                            if event["summary"] == postEvent["title"]:
                                await send_message(instagram_id, f"Event already exists on your calendar {val.get('message')}")
                                return {"status": "ok"}
                            await send_message(instagram_id, f"Another event already exists at that time, adding event anyway but please check your calendar!")
                            #TODO later on maybe change this ask if they want to remove one of the events or keep both
                            return {"status": "ok"}
                    await create_event(user.google_refresh_token, {"title": postEvent["title"], "location": postEvent["location"], "description": postEvent["description"], "start_datetime": val.get('date'), "end_datetime": val.get('date')})
                    val['message'] = f"{val.get('message')} for {postEvent['title']} event"
                    await send_message(instagram_id, f"Event created on your calendar {val.get('message')}")
                    return {"status": "ok"}

        return {"status": "ok"}
    except Exception as e:
        print("Caught error in receive message: ", e)
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


async def get_event_details(caption: str) -> dict:

    try:
        response = client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a marketer who creates engaging event titles based on Instagram post captions. Given a caption, generate a catchy and concise event title that captures the essence of the post. No more than 6 words. Do not include any hashtags or emojis in the title. Your response will be a json with the firstelement called title holding the value which will be the event name you create. You will also include location and description if you can extract it, if not still include these elements but leave them as empty strings. "
                },
                {
                    "role": "user",
                    "content": f"Caption: {caption}"
                }
            ],
            temperature = 0.0,
            response_format={"type": "json_object"}
        )
        output = response.choices[0].message.content

        return output
    except Exception as e:
        print(f"Error in get_event_details: {e}")
        return ""

@router.get("/webhook")
async def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    InstaBot.handle_verify(hub_challenge, hub_verify_token)



