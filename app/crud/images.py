from sqlmodel import Session

from app import models

from .base import BaseCRUD


class VideoCRUD(BaseCRUD[models.Video, models.VideoCreate, models.VideoUpdate]):
    async def create_with_owner_id(
        self, db: Session, *, obj_in: models.VideoCreate, owner_id: str
    ) -> models.Video:
        """
        Create a new video with an owner_id.

        Args:
            db (Session): The database session.
            obj_in (models.VideoCreate): The video to create.
            owner_id (str): The owner_id to set on the video.

        Returns:
            models.Video: The created video.
        """
        obj_in.owner_id = owner_id
        return await self.create(db, obj_in=obj_in)

    async def get_multi_by_owner_id(
        self, db: Session, *, owner_id: str, skip: int = 0, limit: int = 100
    ) -> list[models.Video]:
        """
        Retrieve multiple videos by owner_id.

        Args:
            db (Session): The database session.
            owner_id (str): The owner_id to filter by.
            skip (int): The number of rows to skip. Defaults to 0.
            limit (int): The maximum number of rows to return. Defaults to 100.

        Returns:
            list[models.Video]: A list of videos that match the given criteria.
        """
        return await self.get_multi(db=db, owner_id=owner_id, skip=skip, limit=limit)


video = VideoCRUD(models.Video)
