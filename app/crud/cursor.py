from sqlalchemy import func
from sqlmodel import Session

from app import models

from .base import BaseCRUD


class CursorCRUD(BaseCRUD[models.Cursor, models.CursorCreate, models.CursorRead]):
    async def get_latest(self, db: Session) -> models.Cursor:
        """Get the most recent cursor"""
        results = await self.get_multi(db=db, skip=0, limit=1)
        if not results:
            raise ValueError("No cursors found")
        return results[0]

    async def get_page(self, db: Session, page: int, per_page: int = 10) -> list[models.Cursor]:
        """Get a page of cursors"""
        skip = (page - 1) * per_page
        return await self.get_multi(db=db, skip=skip, limit=per_page)

    async def get_total_pages(self, db: Session, per_page: int = 10) -> int:
        """Get total number of pages"""
        total = await self.count(db=db)
        return (total + per_page - 1) // per_page

    async def create(self, db: Session, *, obj_in: models.CursorCreate) -> models.Cursor:
        # Get the total count of cursors
        total_count = db.query(func.count(models.Cursor.id)).scalar() or 0

        # Create new cursor with page number counting down from total + 1
        db_obj = models.Cursor(
            id=obj_in.id,
            next_cursor_id=obj_in.next_cursor_id,
            created_at=obj_in.created_at,
            page_number=total_count + 1,  # This will be the highest number for the newest cursor
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


cursor = CursorCRUD(models.Cursor)
