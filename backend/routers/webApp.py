from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from bot import InstaBot
from db.models import User
from dependencies import get_current_user
from routers.auth import create_jwt
from jose import jwt
from bot.calendar import list_events

router = APIRouter(prefix = "/api")

@router.post("/sign-up")
async def sign_up(request: Request, db: AsyncSession = Depends(get_db)):
    
    try:
        body = await request.json()
        email = body.get("email")
        instagram_username = body.get("instagram_username")
        
        if not email or not instagram_username:
            return {"error": "Email and Instagram username are required"}
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.google_email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return {"error": "User with this email already exists"}
        
        # Create new user
        new_user = User(google_email=email, instagram_username=instagram_username)
        db.add(new_user)
        await db.commit()

        result = await db.execute(
            select(User).where(User.google_email == user_info["email"])
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise Exception("User not found after creation")
        
        token = create_jwt(user.id)
        return {"token": token}
    except Exception as e:
        print(f"Error in sign-up: {e}")
        return {"message": "Error occurred in creating user", "error": str(e)}

@router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        email = body.get("email")
        
        if not email:
            return {"error": "Email is required"}
        
        # Check if user exists
        result = await db.execute(select(User).where(User.google_email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"error": "User with this email does not exist"}
        
        token = create_jwt(user.id)
        return {"token": token}
    except Exception as e:
        print(f"Error in login: {e}")
        return {"message": "Error occurred in login", "error": str(e)}

@router.get("/test")
async def test(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == 5))
    user = result.scalar_one_or_none()

    events = list_events(user.google_refresh_token)
    
    return {"message": "Test successful"}

    



# @router.get("/me")
# async def get_me(current_user: User = Depends(get_current_user)):
#     return {
#         "email": current_user.google_email,
#         "instagram": current_user.instagram_username
#     }
# example of using jwt from dependencies.py