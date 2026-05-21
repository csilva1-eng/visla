import os
from dotenv import load_dotenv
from dateutil import parser as dateparser
import base64
import requests
from google.cloud import vision
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hmac, hashlib
from db.models import User

load_dotenv()

def handle_verify(
    hub_challenge: str,
    hub_verify_token: str
):
    if hub_verify_token == os.getenv("VERIFY_TOKEN"):
        return PlainTextResponse(content=hub_challenge)
    return PlainTextResponse(status_code=403)

# @app.post("/webhook")
async def handle_message(body: dict):
    
    try:
       
        message = body.get('entry')[0]['messaging'][0]['message']
        if message.get('text'):
            date = extract_date_from_text(message['text'])
            if date:
                formatted = date.strftime("%Y-%m-%dT%H:%M:%S")
                return {"date": formatted, 'message': f"on {date}",
                    "caption": None}
            
        
        for attachment in message['attachments']:
            if attachment['type'] == 'ig_post':
                caption = attachment["payload"]["title"]
                ig_post_media_id = attachment['payload']['ig_post_media_id']
                date = extract_date_from_text(caption)

                if not date:
                    image_url = attachment["payload"]['url']
                    print("no date in text, trying image...")
                    
                    date = await extract_date_from_image(image_url)
                if date is None:
                    return {"message": "Sorry I couldn't find the date, try sending it to me instead in this format '2026-07-25' ",
                    "caption": caption, "date": None}
               
                formatted = date.strftime("%Y-%m-%dT%H:%M:%S")
               
                return {"date": formatted,
                    "caption": caption, 'message': f"on {date}"}


        # if attachment.get("type") == "image":
        #     image_url = attachment.get("payload", {}).get("url")
        #     print(f"Image from {sender_id}: {image_url}")
        return None
        # pretty sure this doesnt actually check if the date is returned just if error thrown
    except Exception as e:
        print(f"Error handling message: {e}")
        return None


# TODO calendar needs this structure to be sent
# {
#     "title": "Indie Night at The Social",
#     "location": "The Social, Orlando FL",
#     "description": "Live music, $10 cover",
#     "start_datetime": "2026-05-24T21:00:00",
#     "end_datetime": "2026-05-24T23:00:00"
# }

def extract_date_from_text(text: str):
    if not text:
        return None
    try:
        datePatterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b',
            r'\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?\b',
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?\b'
        ]

        timePatterns = [
            r'\b\d{1,2}:\d{2}\s*(?:am|pm)\b',           # 4:00pm, 4:00 pm
            r'\b\d{1,2}\s*(?:am|pm)\b',                   # 4pm, 4 am
            r'\b\d{1,2}:\d{2}\s*(?:am|pm)?\s*[-–]\s*\d{1,2}:\d{2}\s*(?:am|pm)\b',  # 4:00-5:00pm, 4:00pm-5:00pm
            r'\b\d{1,2}\s*(?:am|pm)?\s*[-–]\s*\d{1,2}\s*(?:am|pm)\b',              # 4-5pm, 4pm-5pm
            r'\b\d{1,2}:\d{2}\b',                         # 4:00 (no am/pm)
            r'\b(?:noon|midnight)\b',                      # noon, midnight
            r'\b\d{1,2}:\*{2}\s*(?:am|pm)\b'
        ]

        date_result = None
        time_result = None

        for pattern in datePatterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_result = dateparser.parse(match.group())
                break

        range_pattern = r'(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)'
        match = re.search(range_pattern, text, re.IGNORECASE)
        if match:
            start_hour = match.group(1)
            meridiem_raw = match.group(3).replace(".", "").replace(" ", "").upper()
            time_str = f"{start_hour} {meridiem_raw}"
            time_result = dateparser.parse(time_str)
        else:
            for pattern in timePatterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    time_result = dateparser.parse(match.group())
                    break

        if date_result and time_result:
            return date_result.replace(
                hour=time_result.hour,
                minute=time_result.minute
            )
        
        return date_result  

    except Exception as e:
        print("Error in extract from text: ", e)
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