from fastapi import APIRouter

from python_fastapi_stack.api.v1.endpoints import login, users, video

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/user", tags=["Users"])
api_router.include_router(video.router, prefix="/video", tags=["Videos"])
