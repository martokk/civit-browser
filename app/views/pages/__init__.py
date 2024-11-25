from fastapi import APIRouter

from . import account, generation, imagess, login, root, settings, user

router = APIRouter()

router.include_router(root.router)
router.include_router(login.router)
router.include_router(account.router, prefix="/account")
router.include_router(user.router, prefix="/user")
router.include_router(imagess.router)
router.include_router(generation.router)
router.include_router(settings.router)

__all__ = ["router"]
