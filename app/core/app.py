from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from sqlmodel import Session

from app import logger, settings, version
from app.api import deps
from app.api.v1.api import api_router
from app.core import notify
from app.db.init_db import init_initial_data
from app.paths import STATIC_PATH
from app.views.router import views_router

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=version,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    debug=settings.DEBUG,
)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(views_router)

# STATIC_PATH.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_PATH))


@app.on_event("startup")  # type: ignore
async def on_startup(db: Session = next(deps.get_db())) -> None:
    """
    Event handler that gets called when the application starts.
    Logs application start and creates database and tables if they do not exist.

    Args:
        db (Session): Database session.
    """
    logger.info("--- Start FastAPI ---")
    logger.debug("Starting FastAPI App...")
    await init_initial_data(db=db)

    if settings.NOTIFY_ON_START:
        await notify.notify(text=f"{settings.PROJECT_NAME}('{settings.ENV_NAME}') started.")


@app.on_event("startup")  # type: ignore
@repeat_every(seconds=120, wait_first=False)
async def repeating_task() -> None:
    logger.debug("This is a repeating task example that runs every 120 seconds.")
