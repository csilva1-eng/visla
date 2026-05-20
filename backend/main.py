from fastapi import FastAPI
from routers import webhook, auth, webApp
from db.database import engine, Base
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting...")

    yield

    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(webhook.router)
app.include_router(auth.router)
app.include_router(webApp.router)
