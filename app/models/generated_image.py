from typing import TYPE_CHECKING

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from .common import TimestampModel

if TYPE_CHECKING:
    from .cursor import Cursor


class GeneratedImageBase(SQLModel):
    """Base model for generated images."""

    id: str = Field(primary_key=True)
    url: str = Field(index=True)
    width: int
    height: int
    cursor_id: str = Field(foreign_key="cursor.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)


class GeneratedImage(GeneratedImageBase, TimestampModel, table=True):
    """Generated image model for database."""

    __tablename__ = "generated_image"
    cursor: "Cursor" = Relationship(back_populates="images")


class GeneratedImageCreate(GeneratedImageBase):
    """Model for creating generated images."""

    pass


class GeneratedImageRead(GeneratedImageBase):
    """Model for reading generated images."""

    pass
