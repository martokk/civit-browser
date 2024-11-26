from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from .common import TimestampModel


class SettingsBase(SQLModel):
    """Base model for settings."""

    id: str = Field(primary_key=True)
    cookie_string: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)


class Settings(SettingsBase, TimestampModel, table=True):
    """Settings model for database."""

    __tablename__ = "settings"


class SettingsCreate(SettingsBase):
    """Model for creating settings."""

    pass


class SettingsRead(SettingsBase):
    """Model for reading settings."""

    pass
