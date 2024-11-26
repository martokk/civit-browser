from typing import TYPE_CHECKING, Optional

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from .common import TimestampModel

if TYPE_CHECKING:
    from .generated_image import GeneratedImage


class CursorBase(SQLModel):
    """Base model for cursors."""

    id: str = Field(primary_key=True)
    next_cursor_id: Optional[str] = Field(default=None, foreign_key="cursor.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)


class Cursor(CursorBase, TimestampModel, table=True):
    """Cursor model for database."""

    images: list["GeneratedImage"] = Relationship(back_populates="cursor")
    next_cursor: Optional["Cursor"] = Relationship(
        back_populates="previous_cursor",
        sa_relationship_kwargs={
            "remote_side": lambda: [Cursor.id],
            "primaryjoin": "Cursor.next_cursor_id==Cursor.id",
        },
    )
    previous_cursor: Optional["Cursor"] = Relationship(
        back_populates="next_cursor",
        sa_relationship_kwargs={"remote_side": lambda: [Cursor.next_cursor_id]},
    )
    page_number: Optional[int] = Field(default=None)


class CursorCreate(CursorBase):
    """Model for creating cursors."""

    pass


class CursorRead(CursorBase):
    """Model for reading cursors."""

    pass
