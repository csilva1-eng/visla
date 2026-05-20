import os
from dotenv import load_dotenv
from dateutil import parser as dateparser
import base64
import requests
from google.cloud import vision
import re
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hmac, hashlib
from db.models import User

load_dotenv()

def handle_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    if hub_verify_token == os.getenv("VERIFY_TOKEN"):
        return PlainTextResponse(content=hub_challenge)
    return PlainTextResponse(status_code=403)

SHAX_ID = os.getenv("SHAX_ID")
#TODO THIS MIGHT NEED quotes?

# @app.post("/webhook")
async def handle_message(body: dict, instagram_id: str, db: AsyncSession):
    
    try:
        messaging = body.get('entry')[0]['messaging'][0]
        if "read" in messaging:
            return
        if "delivery" in messaging:
            return

        if "message" not in messaging:
            return
            
        if messaging["message"].get("is_echo"):
            return
        # message_text = body.get("entry").get("messaging").get("message").get("text")
        
        result = await db.execute(select(User).where(User.instagram_id == str(instagram_id)))
        user = result.scalar_one_or_none()

        if not user:
            return f"Welcome to Visla, to get started click {generate_onboarding_link(str(instagram_id))}"
        
        for entry in body.get("entry", []):
            if entry.get("id") != SHAX_ID:
                continue

            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {})
                
                text = message.get("text")
                attachments = message.get("attachments", [])

                if sender_id:
                    if text:
                        print(f"Message from {sender_id}: {text}")
                    
                    for attachment in attachments:
                        if attachment.get("type") == "ig_post":
                            image_url = attachment.get("payload", {}).get("url")
                            title = attachment.get("payload", {}).get("title")

                            date = extract_date_from_text(title)

                            if not date:
                                print("no date in text, trying image...")
                                # trying to get from image
                                date = await extract_date_from_image(image_url)
                            return f"Date found: {date}"
                            # print(f"Instagram post from {sender_id}: {image_url}")
                        if attachment.get("type") == "image":
                            image_url = attachment.get("payload", {}).get("url")
                            print(f"Image from {sender_id}: {image_url}")
        return ""
        # pretty sure this doesnt actually check if the date is returned just if error thrown
    except Exception as e:
        print(f"Error handling message: {e}")
        return False


def extract_date_from_text(text: str):
    if not text:
        return None
    try:
        # common date patterns
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b',
            r'\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?\b',
            r'\b\d{1,2}(?::\d{2})?(?:am|pm)?[-–]\d{1,2}(?::\d{2})?(?:am|pm)\b',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?\b'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return dateparser.parse(match.group())
    except Exception:
        return None
    return None

async def extract_date_from_image(image_url: str):
    try:
        res = requests.get(image_url)
        content = base64.b64encode(res.content).decode("utf-8")

        response = requests.post(
            f"https://vision.googleapis.com/v1/images:annotate?key={os.getenv("VISION_API_KEY")}",
            json={
                "requests": [{
                    "image": {"content": content},
                    "features": [{"type": "TEXT_DETECTION"}]
                }]
            }
        )

        result = response.json()
        print("status:", response.status_code)

        # check for errors
        if "error" in result:
            print("error:", result["error"])
            return None

        full_text = result["responses"][0]["textAnnotations"][0]["description"]
        print("raw text:", full_text)
        return extract_date_from_text(full_text)
    except Exception as e:
        print("error: ", e)
        return None
    return None

def generate_onboarding_link(instagram_id: str) -> str:
    sig = hmac.new(os.getenv("LINK_SECRET").encode(), instagram_id.encode(), hashlib.sha256).hexdigest()[:12]
    return f"{os.getenv('FRONTEND_URL')}/?ig_id={instagram_id}&sig={sig}"

def verify_link(instagram_id: str, sig: str) -> bool:
    expected = hmac.new(os.getenv("LINK_SECRET").encode(), instagram_id.encode(), hashlib.sha256).hexdigest()[:12]
    return hmac.compare_digest(expected, sig)