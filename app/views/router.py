from fastapi import APIRouter

from app.views.pages import account, login, root, user, imagess

views_router = APIRouter(include_in_schema=False)
views_router.include_router(root.router, tags=["Views"])
views_router.include_router(imagess.router, tags=["Imagess"])
views_router.include_router(login.router, tags=["Logins"])
views_router.include_router(account.router, prefix="/account", tags=["Account"])
views_router.include_router(user.router, prefix="/user", tags=["Users"])
