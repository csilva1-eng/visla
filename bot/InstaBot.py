from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
from dateutil import parser as dateparser
import base64
import requests
from google.cloud import vision
import re

load_dotenv()

app = FastAPI()


# example link https://lookaside.fbsbx.com/ig_messaging_cdn/?asset_id=17939507193037650&signature=Ab3aNHk3RKeh5NUdoFwU17gcxp37PdZlphZtqtqEyzrMaCcwin0kjMcMSTeeYu002SU6ISzGAmIeXibJksyigkmadJsMlwDxY2ebfE9etx6Cex-JTqoA573M9Ccg8wKuMzHdEqeZacsgQxIs4145dz5Jnv7mDJZRoeum7a8_zs-BhCVf4UR5gKWrcFplHB1aVlmKqd4P2x1Y6kOYz53809FIvLwiLsmJ'

@app.get("/webhook")
def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    if hub_verify_token == os.getenv("VERIFY_TOKEN"):
        return PlainTextResponse(content=hub_challenge)
    return PlainTextResponse(status_code=403)

SHAX_ID = "17841417217256759"

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json() 
    print(body)

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
                            date = extract_date_from_image(image_url)
                        print(f"date foudn: {date}")
                        # print(f"Instagram post from {sender_id}: {image_url}")
                    if attachment.get("type") == "image":
                        image_url = attachment.get("payload", {}).get("url")
                        print(f"Image from {sender_id}: {image_url}")

    return {"status": "ok"}


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

def extract_date_from_image(image_url: str):
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