from sqlmodel import Session

from app import models

from .base import BaseCRUD


class SettingsCRUD(BaseCRUD[models.Settings, models.SettingsCreate, models.SettingsRead]):
    async def get_current(self, db: Session) -> models.Settings:
        """Get current settings"""
        results = await self.get_multi(db=db, skip=0, limit=1)
        if not results:
            # Create default settings
            settings_create = models.SettingsCreate(id="current", cookie_string="")
            return await self.create(db, obj_in=settings_create)
        return results[0]


settings = SettingsCRUD(models.Settings)
