from datetime import datetime

from sqlalchemy import desc, func
from sqlmodel import Session, select

from app import models

from .base import BaseCRUD


def extract_timestamp_from_cursor_id(cursor_id: str) -> datetime:
    """Extract timestamp from cursor ID format: modelid-YYYYMMDDHHmmssSSS"""
    timestamp_str = cursor_id.split("-")[1]
    # Parse YYYYMMDDHHmmssSSS format
    return datetime.strptime(timestamp_str[:14], "%Y%m%d%H%M%S")


class CursorCRUD(BaseCRUD[models.Cursor, models.CursorCreate, models.CursorRead]):
    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[models.Cursor]:
        """Get multiple cursors ordered by timestamp in ID descending"""
        stmt = select(models.Cursor).order_by(desc(models.Cursor.id)).offset(skip).limit(limit)
        result = db.execute(stmt).all()
        return [r[0] for r in result]

    async def get_latest(self, db: Session) -> models.Cursor:
        """Get the most recent cursor based on the timestamp in the ID"""
        # Extract timestamp from cursor ID and order by it
        stmt = select(models.Cursor).order_by(desc(models.Cursor.id))
        result = db.execute(stmt).first()
        if not result:
            raise ValueError("No cursors found")
        return result[0]

    async def get_page(self, db: Session, page: int, per_page: int = 10) -> list[models.Cursor]:
        """Get a page of cursors ordered by timestamp in ID descending"""
        skip = (page - 1) * per_page
        stmt = select(models.Cursor).order_by(desc(models.Cursor.id)).offset(skip).limit(per_page)
        result = db.execute(stmt).all()
        return [r[0] for r in result]

    async def get_total_pages(self, db: Session, per_page: int = 10) -> int:
        """Get total number of pages"""
        total = await self.count(db=db)
        return (total + per_page - 1) // per_page

    async def create(self, db: Session, *, obj_in: models.CursorCreate) -> models.Cursor:
        # Get all cursors ordered by ID (which contains timestamp) descending
        stmt = select(models.Cursor).order_by(desc(models.Cursor.id))
        existing_cursors = db.execute(stmt).all()
        existing_cursors = [r[0] for r in existing_cursors]

        # If this is the first cursor, its page number will be 1
        if not existing_cursors:
            page_number = 1
        else:
            # Find where this cursor should be inserted based on its ID
            # The ID format is: modelid-YYYYMMDDHHmmssSSS
            new_cursor_timestamp = obj_in.id.split("-")[1]
            insert_position = 0

            for i, cursor in enumerate(existing_cursors):
                existing_timestamp = cursor.id.split("-")[1]
                if new_cursor_timestamp > existing_timestamp:
                    insert_position = i
                    break
                insert_position = i + 1

            # Page number will be insert_position + 1
            page_number = insert_position + 1

            # Update page numbers for all cursors that come after this one
            for cursor in existing_cursors[insert_position:]:
                cursor.page_number = cursor.page_number + 1
                db.add(cursor)

        # Extract timestamp from cursor ID
        created_at = extract_timestamp_from_cursor_id(obj_in.id)

        # Create new cursor with calculated page number and extracted timestamp
        db_obj = models.Cursor(
            id=obj_in.id,
            next_cursor_id=obj_in.next_cursor_id,
            created_at=created_at,
            page_number=page_number,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


cursor = CursorCRUD(models.Cursor)
