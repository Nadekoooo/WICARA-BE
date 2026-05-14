from fastapi import APIRouter

from app.api.v1 import auth, curriculum

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(curriculum.router, tags=["curriculum"])
