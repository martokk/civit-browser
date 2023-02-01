from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from python_fastapi_stack import models, settings
from python_fastapi_stack.views import deps

router = APIRouter()
templates = Jinja2Templates(directory="python_fastapi_stack/views/templates")


@router.get("/", response_class=HTMLResponse)
async def root_index_router(
    request: Request,
    current_user: models.User = Depends(deps.get_current_user),
) -> Response:
    """
    Home page router

    Args:
        request(Request): The request object
        current_user(models.User): The current user

    Returns:
        Response: Home page
    """
    if current_user:
        return await root_index_authenticated(request, current_user)
    return await root_index_unauthenticated(request)


async def root_index_unauthenticated(
    request: Request,
) -> Response:
    """
    Home page (Not authenticated)

    Args:
        request(Request): The request object

    Returns:
        Response: Home page
    """
    return RedirectResponse(url="/login")


async def root_index_authenticated(
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """
    Home page. (Authenticated)

    Args:
        request(Request): The request object
        current_user(models.User): The current user

    Returns:
        Response: Home page
    """
    title = f"{settings.PROJECT_NAME} - Home"
    message = f"Welcome to the {settings.PROJECT_NAME}, {current_user.username}!"
    context = {"request": request, "current_user": current_user, "title": title, "message": message}
    return templates.TemplateResponse("root/home.html", context=context)
