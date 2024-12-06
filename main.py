from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.db import database
from routers import auth_router, activity_router, friend_router
from routers import dashboard_router

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(dashboard_router.router, prefix="/personal", tags=["personal"])
app.include_router(activity_router.router, prefix="/activity", tags=["dashboard"])
app.include_router(friend_router.router, prefix="/friend", tags=["friend"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}
