from fastapi import FastAPI
# from routers import webhook, auth
# from database import engine, Base

app = FastAPI()

# app.include_router(webhook.router)
# app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

