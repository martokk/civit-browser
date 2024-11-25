from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates

router = APIRouter()


@router.get("/imagess", response_class=HTMLResponse)
async def list_imagess(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Returns HTML response with list of imagess.

    Args:
        request(Request): The request object
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: HTML page with the imagess

    """
    # Get alerts dict from cookies
    alerts = models.Alerts().from_cookies(request.cookies)

    imagess = await crud.images.get_multi(db=db, owner_id=current_user.id)
    return templates.TemplateResponse(
        "images/list.html",
        {"request": request, "imagess": imagess, "current_user": current_user, "alerts": alerts},
    )


@router.get("/imagess/all", response_class=HTMLResponse)
async def list_all_imagess(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_superuser
    ),
) -> Response:
    """
    Returns HTML response with list of all imagess from all users.

    Args:
        request(Request): The request object
        db(Session): The database session.
        current_user(User): The authenticated superuser.

    Returns:
        Response: HTML page with the imagess

    """
    # Get alerts dict from cookies
    alerts = models.Alerts().from_cookies(request.cookies)

    imagess = await crud.images.get_all(db=db)
    return templates.TemplateResponse(
        "images/list.html",
        {"request": request, "imagess": imagess, "current_user": current_user, "alerts": alerts},
    )


@router.get("/images/{images_id}", response_class=HTMLResponse)
async def view_images(
    request: Request,
    images_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    View images.

    Args:
        request(Request): The request object
        images_id(str): The images id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: View of the images
    """
    alerts = models.Alerts()
    try:
        images = await crud.images.get(db=db, id=images_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Images not found")
        response = RedirectResponse("/imagess", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    return templates.TemplateResponse(
        "images/view.html",
        {"request": request, "images": images, "current_user": current_user, "alerts": alerts},
    )


@router.get("/imagess/create", response_class=HTMLResponse)
async def create_images(
    request: Request,
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Images form.

    Args:
        request(Request): The request object
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new images
    """
    alerts = models.Alerts().from_cookies(request.cookies)
    return templates.TemplateResponse(
        "images/create.html",
        {"request": request, "current_user": current_user, "alerts": alerts},
    )


@router.post("/imagess/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def handle_create_images(
    title: str = Form(...),
    description: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Handles the creation of a new images.

    Args:
        title(str): The title of the images
        description(str): The description of the images
        url(str): The url of the images
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: List of imagess view
    """
    alerts = models.Alerts()
    images_create = models.ImagesCreate(
        title=title, description=description, url=url, owner_id=current_user.id
    )
    try:
        await crud.images.create(db=db, obj_in=images_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Images already exists")
        response = RedirectResponse("/imagess/create", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Images successfully created")
    response = RedirectResponse(url="/imagess", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.get("/images/{images_id}/edit", response_class=HTMLResponse)
async def edit_images(
    request: Request,
    images_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Images form.

    Args:
        request(Request): The request object
        images_id(str): The images id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new images
    """
    alerts = models.Alerts().from_cookies(request.cookies)
    try:
        images = await crud.images.get(db=db, id=images_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Images not found")
        response = RedirectResponse("/imagess", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    return templates.TemplateResponse(
        "images/edit.html",
        {"request": request, "images": images, "current_user": current_user, "alerts": alerts},
    )


@router.post("/images/{images_id}/edit", response_class=HTMLResponse)
async def handle_edit_images(
    request: Request,
    images_id: str,
    title: str = Form(...),
    description: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Handles the creation of a new images.

    Args:
        request(Request): The request object
        images_id(str): The images id
        title(str): The title of the images
        description(str): The description of the images
        url(str): The url of the images
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: View of the newly created images
    """
    alerts = models.Alerts()
    images_update = models.ImagesUpdate(title=title, description=description, url=url)

    try:
        new_images = await crud.images.update(db=db, obj_in=images_update, id=images_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Images not found")
        response = RedirectResponse(url="/imagess", status_code=status.HTTP_303_SEE_OTHER)
        response.headers["Method"] = "GET"
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    alerts.success.append("Images updated")
    return templates.TemplateResponse(
        "images/edit.html",
        {"request": request, "images": new_images, "current_user": current_user, "alerts": alerts},
    )


@router.get("/images/{images_id}/delete", response_class=HTMLResponse)
async def delete_images(
    images_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Images form.

    Args:
        images_id(str): The images id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new images
    """
    alerts = models.Alerts()
    try:
        await crud.images.remove(db=db, id=images_id)
        alerts.success.append("Images deleted")
    except crud.RecordNotFoundError:
        alerts.danger.append("Images not found")
    except crud.DeleteError:
        alerts.danger.append("Error deleting images")

    response = RedirectResponse(url="/imagess", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response
