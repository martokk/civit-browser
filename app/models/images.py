from typing import TYPE_CHECKING, Any

import datetime

from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from app.core.uuid import generate_uuid_from_url

from .common import TimestampModel

if TYPE_CHECKING:
    from .user import User  # pragma: no cover


class VideoBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    title: str = Field(default=None)
    description: str = Field(default=None)
    url: str = Field(default=None)
    owner_id: str = Field(foreign_key="user.id", nullable=False, default=None)


class Video(VideoBase, table=True):
    owner: "User" = Relationship(back_populates="videos")


class VideoCreate(VideoBase):
    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        sanitized_url = values["url"]
        video_uuid = generate_uuid_from_url(url=sanitized_url)
        return {
            **values,
            "url": sanitized_url,
            "id": values.get("id", video_uuid),
            "updated_at": datetime.datetime.now(tz=datetime.timezone.utc),
        }


class VideoUpdate(VideoBase):
    pass


class VideoRead(VideoBase):
    pass
