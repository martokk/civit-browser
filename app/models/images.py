from typing import TYPE_CHECKING, Any, ClassVar

from datetime import datetime, timezone

from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from app.core.uuid import generate_uuid_from_url

from .common import TimestampModel

if TYPE_CHECKING:
    from .user import User


class ImagesBase(SQLModel):
    """Base model for images."""

    id: str = Field(default=None, primary_key=True)
    title: str = Field(default=None)
    description: str = Field(default=None)
    url: str = Field(default=None)
    owner_id: str = Field(foreign_key="user.id", nullable=False, default=None)


class Images(ImagesBase, TimestampModel, table=True):
    """Images model for database."""

    owner: "User" = Relationship(back_populates="imagess")


class ImagesCreate(ImagesBase):
    """Model for creating images."""

    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls: ClassVar, values: dict[str, Any]) -> dict[str, Any]:
        """Set default values before validation."""
        sanitized_url = values["url"]
        images_uuid = generate_uuid_from_url(url=sanitized_url)
        return {
            **values,
            "url": sanitized_url,
            "id": values.get("id", images_uuid),
            "updated_at": datetime.now(timezone.utc),
        }


class ImagesUpdate(ImagesBase):
    """Model for updating images."""

    pass


class ImagesRead(ImagesBase):
    """Model for reading images."""

    pass
