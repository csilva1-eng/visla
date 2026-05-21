from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

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