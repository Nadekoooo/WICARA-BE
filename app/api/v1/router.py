from fastapi import APIRouter

from app.api.v1 import auth, curriculum, learning, me, profile, workspaces

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(curriculum.router, tags=["curriculum"])
api_router.include_router(learning.router, tags=["learning"])
api_router.include_router(me.router, tags=["me"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(workspaces.router, tags=["workspaces"])
