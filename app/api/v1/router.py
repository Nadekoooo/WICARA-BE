from fastapi import APIRouter

from app.api.v1 import curriculum

api_router = APIRouter()
api_router.include_router(curriculum.router, tags=["curriculum"])
