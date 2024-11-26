from sqlmodel import Session

from app import models

from .base import BaseCRUD


class GeneratedImageCRUD(
    BaseCRUD[models.GeneratedImage, models.GeneratedImageCreate, models.GeneratedImageRead]
):
    async def get_by_cursor(
        self, db: Session, cursor_id: str, skip: int = 0, limit: int = 100
    ) -> list[models.GeneratedImage]:
        """Get all images for a cursor"""
        return await self.get_multi(db=db, cursor_id=cursor_id, skip=skip, limit=limit)


generated_image = GeneratedImageCRUD(models.GeneratedImage)
