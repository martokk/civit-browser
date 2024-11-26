from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates

router = APIRouter()


@router.get("/settings", response_class=HTMLResponse)
async def view_settings(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """Settings page view"""
    settings = await crud.settings.get_current(db)
    alerts = models.Alerts.from_cookies(request.cookies)
    context = {
        "request": request,
        "current_user": current_user,
        "settings": settings,
        "alerts": alerts,
    }
    return templates.TemplateResponse("settings/view.html", context=context)


@router.post("/settings", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    cookie_string: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """Update settings"""
    alerts = models.Alerts()

    # Validate cookie string
    if "__Secure-civitai-token" not in cookie_string:
        alerts.danger.append("Invalid cookie string - must contain civitai token")
        response = RedirectResponse("/settings", status_code=302)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    settings = await crud.settings.get_current(db)

    # Update settings
    settings_update = models.SettingsRead(
        id=settings.id, cookie_string=cookie_string, created_at=settings.created_at
    )
    await crud.settings.update(db, obj_in=settings_update, id=settings.id)

    alerts.success.append("Settings updated successfully")
    response = RedirectResponse("/settings", status_code=302)
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response
