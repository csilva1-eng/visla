from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google_auth_oauthlib.flow import Flow
from jose import jwt
from datetime import datetime, timedelta
import os
from database import get_db
from models import User

router = APIRouter(prefix="/auth")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar"
]

def create_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )

def create_jwt(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

@router.get("/google")
async def google_login():
    flow = create_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",   # gives us a refresh token
        prompt="consent"         # forces refresh token every time
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    flow = create_flow()
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    
    # Get user info from Google
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"}
        )
    user_info = response.json()
    
    # Find or create user in DB
    result = await db.execute(
        select(User).where(User.google_email == user_info["email"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            google_email=user_info["email"],
            google_refresh_token=credentials.refresh_token
        )
        db.add(user)
    else:
        user.google_refresh_token = credentials.refresh_token
        user.last_active = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    # Create JWT and redirect back to frontend
    token = create_jwt(user.id)
    return RedirectResponse(
        f"{os.getenv('FRONTEND_URL')}/auth/success?token={token}"
    )