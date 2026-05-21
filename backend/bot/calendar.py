from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from datetime import datetime
from zoneinfo import ZoneInfo

def get_calendar_service(refresh_token: str):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
    )
    
    # Auto refresh the access token using the refresh token
    creds.refresh(Request())
    
    return build("calendar", "v3", credentials=creds)

async def create_event(refresh_token: str, event_details: dict):
    try:
        service = get_calendar_service(refresh_token)
        
        event = {
            "summary": event_details.get("title"),
            "location": event_details.get("location"),
            "description": event_details.get("description"),
            "start": {
                "dateTime": event_details.get("start_datetime"),
                "timeZone": "America/New_York"
            },
            "end": {
                "dateTime": event_details.get("end_datetime"),
                "timeZone": "America/New_York"
            }
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        print("Event created:", created_event.get("htmlLink"))
        return created_event

    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None

async def list_events(refresh_token: str):
    try:
        service = get_calendar_service(refresh_token)
        

        #TODO in future make this be based on users current location? or location insta account is based in
        now = datetime.now(ZoneInfo("America/New_York")).isoformat()
        events_result = service.events().list(
            calendarId="primary",
            # timeMin=now,
            timeMin="2026-01-01T00:00:00Z",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        return events

    except Exception as e:
        print(f"Error listing calendar events: {e}")
        return None