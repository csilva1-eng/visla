from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from google_auth_oauthlib.flow import Flow
from jose import jwt
from datetime import datetime, timedelta
import os
from db.database import get_db
from db.models import User
import asyncio
from functools import partial
import httpx
from bot.InstaBot import verify_link

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

router = APIRouter(prefix="/auth")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar"
]

# def create_flow():
#     flow = Flow.from_client_config(
#         {
#             "web": {
#                 "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#                 "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
#                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                 "token_uri": "https://oauth2.googleapis.com/token",
#                 "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
#             }
#         },
#         scopes=SCOPES,
#         redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
#     )
#     flow.oauth2session.code_challenge_method = None
#     return flow

def create_jwt(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

@router.get("/google")
async def google_login(ig_id: str, sig: str):
    print(ig_id)
    print(sig)
    if not verify_link(ig_id, sig):
        raise HTTPException(status_code=403, detail="Invalid or tampered link")

    from urllib.parse import urlencode
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": ig_id
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)
    return RedirectResponse(auth_url)

@router.get("/callback")
async def google_callback(code: str, state: str, db: AsyncSession = Depends(get_db)):
    # Exchange code for tokens manually - no Flow needed
    try:
            
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
                    "grant_type": "authorization_code"
                }
            )
        
        tokens = token_response.json()
        # print(tokens)  # check what we get back
        
        if "error" in tokens:
            raise HTTPException(status_code=400, detail=tokens["error"])
        
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")

        # Get user info
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        user_info = user_response.json()
        # print(user_info)

        # Find or create user in DB
        print("trying to find user in db")
        result = await db.execute(
            select(User).where(User.google_email == user_info["email"])
        )
        user = result.scalar_one_or_none()
        print("hello user?")
        print(user)
        if not user:
            user = User(
                google_email=user_info["email"],
                google_refresh_token=refresh_token,
                instagram_id = state,
            )
            db.add(user)
        else:
            user.google_refresh_token = refresh_token
            user.last_active = datetime.utcnow()
        print("committing to db...")
        await db.commit()
        await db.refresh(user)

        token = create_jwt(user.id)
        print("trying to go back")
        return RedirectResponse(
            f"{os.getenv('FRONTEND_URL')}/coming-soon/?token={token}"
        )
        #TODO actual dashboard???


    except Exception as e:
        print(f"Error in Google callback: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")