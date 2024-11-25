from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, logger, models
from app.core import civit
from app.views import deps, templates

router = APIRouter()


@router.get("/generation", response_class=HTMLResponse)
async def view_generation(
    request: Request,
    page: int = 1,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """Generation page view"""
    # Get paginated cursors
    page_size = 10
    skip = (page - 1) * page_size
    cursors = await crud.cursor.get_multi(db=db, skip=skip, limit=page_size)
    total = await crud.cursor.count(db=db)
    total_pages = (total + page_size - 1) // page_size

    alerts = models.Alerts.from_cookies(request.cookies)
    context = {
        "request": request,
        "current_user": current_user,
        "cursors": cursors,
        "page": page,
        "total_pages": total_pages,
        "alerts": alerts,
    }
    return templates.TemplateResponse("generation/list.html", context=context)


@router.get("/generation/{cursor_id}", response_class=HTMLResponse)
async def view_cursor(
    request: Request,
    cursor_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """View cursor details"""
    cursor = await crud.cursor.get(db=db, id=cursor_id)
    images = await crud.generated_image.get_multi(db=db, cursor_id=cursor_id)

    alerts = models.Alerts.from_cookies(request.cookies)
    context = {
        "request": request,
        "current_user": current_user,
        "cursor": cursor,
        "images": images,
        "alerts": alerts,
    }
    return templates.TemplateResponse("generation/view.html", context=context)


async def import_cursor_recursive(cursor_id: Optional[str], db: Session) -> tuple[int, int]:
    """
    Recursively import cursor and its images, following the next_cursor chain.
    If cursor_id is None, starts from the most recent cursor.
    Stops after encountering 5 consecutive existing cursors.
    Returns tuple of (cursors_imported, images_imported)
    """
    cursors_imported = 0
    images_imported = 0
    current_cursor_id = cursor_id
    visited_cursors = set()  # Keep track of cursors we've seen to avoid loops
    consecutive_existing = 0  # Counter for consecutive existing cursors

    # Get first cursor data - this will be the latest if cursor_id is None
    cursor_data = await civit.fetch_cursor_data(cursor=current_cursor_id, db=db)
    if not cursor_data:
        logger.warning(f"No data found for cursor {current_cursor_id}")
        return cursors_imported, images_imported

    # If we requested latest (null cursor), get the actual cursor ID from the response
    if current_cursor_id is None:
        current_cursor_id = cursor_data["current_cursor_id"]
        logger.info(f"Starting import from latest cursor: {current_cursor_id}")

    while current_cursor_id and current_cursor_id not in visited_cursors:
        visited_cursors.add(current_cursor_id)

        # Check if cursor exists
        existing_cursor = await crud.cursor.get_or_none(db=db, id=current_cursor_id)
        if existing_cursor:
            consecutive_existing += 1
            logger.info(f"Cursor {current_cursor_id} already exists ({consecutive_existing}/5)")

            if consecutive_existing >= 5:
                logger.info("Found 5 consecutive existing cursors, stopping import")
                break

            current_cursor_id = existing_cursor.next_cursor_id
            continue

        # Reset consecutive counter since we found a new cursor
        consecutive_existing = 0

        # Create cursor record
        cursor_create = models.CursorCreate(
            id=current_cursor_id,
            next_cursor_id=cursor_data.get("next_cursor"),
        )
        cursor = await crud.cursor.create(db=db, obj_in=cursor_create)
        cursors_imported += 1
        logger.info(f"Imported cursor {cursor.id}")

        # Import images for this cursor
        for image_data in cursor_data["images"]:
            # Skip if image already exists
            if await crud.generated_image.get_or_none(db=db, id=image_data["id"]):
                logger.debug(f"Image {image_data['id']} already exists, skipping...")
                continue

            # Create image record
            image_create = models.GeneratedImageCreate(
                id=image_data["id"],
                url=image_data["url"],
                cursor_id=cursor.id,
                width=image_data["width"],
                height=image_data["height"],
                created_at=image_data["completed"],
            )
            await crud.generated_image.create(db=db, obj_in=image_create)
            images_imported += 1
            logger.debug(f"Imported image {image_data['id']}")

        # Move to next cursor
        current_cursor_id = cursor_data.get("next_cursor")
        if current_cursor_id:
            cursor_data = await civit.fetch_cursor_data(cursor=current_cursor_id, db=db)
            if not cursor_data:
                logger.warning(f"No data found for cursor {current_cursor_id}")
                break
        else:
            logger.info("No more cursors to import")
            break

    return cursors_imported, images_imported


@router.post("/generation/import")
async def import_cursor(
    request: Request,
    cursor_id: Annotated[str, Form()] = None,  # Make cursor_id optional
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """Import cursor data recursively. If cursor_id is None, imports from latest."""
    alerts = models.Alerts()

    try:
        cursors_imported, images_imported = await import_cursor_recursive(
            cursor_id=cursor_id, db=db
        )
        alerts.success.append(
            f"Successfully imported {cursors_imported} cursors and {images_imported} images"
        )

    except Exception as e:
        alerts.danger.append(f"Error importing cursor: {str(e)}")

    response = RedirectResponse("/generation", status_code=302)
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response
