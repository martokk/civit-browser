from typing import TYPE_CHECKING, Any

from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from app.core.uuid import generate_uuid_from_string

from .common import TimestampModel

if TYPE_CHECKING:
    from app.models.images import Images


class UserBase(SQLModel):
    """Base model for users."""

    id: str = Field(
        primary_key=True,
        index=True,
        nullable=False,
        default=None,
    )
    username: str = Field(index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    full_name: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class User(UserBase, TimestampModel, table=True):
    """User model for database."""

    __tablename__ = "user"
    hashed_password: str = Field(nullable=False)
    imagess: list["Images"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={
            "cascade": "all, delete",
        },
    )

    class Config:
        table = True


class UserCreate(UserBase):
    """Model for creating users."""

    hashed_password: str = Field(nullable=False)

    @root_validator(pre=True)
    @classmethod
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Set default values before validation."""
        values["id"] = values.get("id", generate_uuid_from_string(string=values["username"]))
        return values


class UserCreateWithPassword(UserBase):
    """Model for creating users with password."""

    password: str = Field(nullable=False)


class UserUpdate(SQLModel):
    """Model for updating users."""

    username: str | None = Field(default=None)
    email: str | None = Field(default=None)
    full_name: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    is_superuser: bool | None = Field(default=None)
    hashed_password: str | None = Field(default=None)


class UserRead(UserBase):
    """Model for reading users."""

    pass


class UserLogin(SQLModel):
    """Model for user login."""

    username: str
    password: str
