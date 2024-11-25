from typing import TYPE_CHECKING, Any

import datetime

from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from app.core.uuid import generate_uuid_from_url

from .common import TimestampModel

if TYPE_CHECKING:
    from .user import User  # pragma: no cover


class ImagesBase(TimestampModel, SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    title: str = Field(default=None)
    description: str = Field(default=None)
    url: str = Field(default=None)
    owner_id: str = Field(foreign_key="user.id", nullable=False, default=None)


class Images(ImagesBase, table=True):
    owner: "User" = Relationship(back_populates="imagess")


class ImagesCreate(ImagesBase):
    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        sanitized_url = values["url"]
        images_uuid = generate_uuid_from_url(url=sanitized_url)
        return {
            **values,
            "url": sanitized_url,
            "id": values.get("id", images_uuid),
            "updated_at": datetime.datetime.now(tz=datetime.timezone.utc),
        }


class ImagesUpdate(ImagesBase):
    pass


class ImagesRead(ImagesBase):
    pass
