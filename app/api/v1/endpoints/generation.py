from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud, models
from app.api import deps
from app.core.civit import fetch_cursor_data

router = APIRouter()


@router.post("/import-generation", response_model=models.CursorRead)
async def import_generation_data(
    cursor_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.Cursor:
    """
    Import generation data from Civitai for a given cursor
    """
    # Fetch cursor data from Civitai
    cursor_data = await fetch_cursor_data(cursor_id, db)
    if not cursor_data:
        raise HTTPException(status_code=404, detail="Cursor not found")

    # Create cursor record
    cursor_create = models.CursorCreate(id=cursor_id, next_cursor_id=cursor_data.get("next_cursor"))
    cursor = await crud.cursor.create(db, obj_in=cursor_create)

    # Create image records
    for image_data in cursor_data.get("images", []):
        image_create = models.GeneratedImageCreate(
            id=image_data["id"],
            url=image_data["url"],
            width=image_data["width"],
            height=image_data["height"],
            cursor_id=cursor.id,
        )
        await crud.generated_image.create(db, obj_in=image_create)

    return cursor
