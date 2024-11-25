from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates

router = APIRouter()


@router.get("/videos", response_class=HTMLResponse)
async def list_videos(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Returns HTML response with list of videos.

    Args:
        request(Request): The request object
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: HTML page with the videos

    """
    # Get alerts dict from cookies
    alerts = models.Alerts().from_cookies(request.cookies)

    videos = await crud.video.get_multi(db=db, owner_id=current_user.id)
    return templates.TemplateResponse(
        "video/list.html",
        {"request": request, "videos": videos, "current_user": current_user, "alerts": alerts},
    )


@router.get("/videos/all", response_class=HTMLResponse)
async def list_all_videos(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_superuser
    ),
) -> Response:
    """
    Returns HTML response with list of all videos from all users.

    Args:
        request(Request): The request object
        db(Session): The database session.
        current_user(User): The authenticated superuser.

    Returns:
        Response: HTML page with the videos

    """
    # Get alerts dict from cookies
    alerts = models.Alerts().from_cookies(request.cookies)

    videos = await crud.video.get_all(db=db)
    return templates.TemplateResponse(
        "video/list.html",
        {"request": request, "videos": videos, "current_user": current_user, "alerts": alerts},
    )


@router.get("/video/{video_id}", response_class=HTMLResponse)
async def view_video(
    request: Request,
    video_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    View video.

    Args:
        request(Request): The request object
        video_id(str): The video id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: View of the video
    """
    alerts = models.Alerts()
    try:
        video = await crud.video.get(db=db, id=video_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Video not found")
        response = RedirectResponse("/videos", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    return templates.TemplateResponse(
        "video/view.html",
        {"request": request, "video": video, "current_user": current_user, "alerts": alerts},
    )


@router.get("/videos/create", response_class=HTMLResponse)
async def create_video(
    request: Request,
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Video form.

    Args:
        request(Request): The request object
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new video
    """
    alerts = models.Alerts().from_cookies(request.cookies)
    return templates.TemplateResponse(
        "video/create.html",
        {"request": request, "current_user": current_user, "alerts": alerts},
    )


@router.post("/videos/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def handle_create_video(
    title: str = Form(...),
    description: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Handles the creation of a new video.

    Args:
        title(str): The title of the video
        description(str): The description of the video
        url(str): The url of the video
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: List of videos view
    """
    alerts = models.Alerts()
    video_create = models.VideoCreate(
        title=title, description=description, url=url, owner_id=current_user.id
    )
    try:
        await crud.video.create(db=db, obj_in=video_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Video already exists")
        response = RedirectResponse("/videos/create", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Video successfully created")
    response = RedirectResponse(url="/videos", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.get("/video/{video_id}/edit", response_class=HTMLResponse)
async def edit_video(
    request: Request,
    video_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Video form.

    Args:
        request(Request): The request object
        video_id(str): The video id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new video
    """
    alerts = models.Alerts().from_cookies(request.cookies)
    try:
        video = await crud.video.get(db=db, id=video_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Video not found")
        response = RedirectResponse("/videos", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    return templates.TemplateResponse(
        "video/edit.html",
        {"request": request, "video": video, "current_user": current_user, "alerts": alerts},
    )


@router.post("/video/{video_id}/edit", response_class=HTMLResponse)
async def handle_edit_video(
    request: Request,
    video_id: str,
    title: str = Form(...),
    description: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Handles the creation of a new video.

    Args:
        request(Request): The request object
        video_id(str): The video id
        title(str): The title of the video
        description(str): The description of the video
        url(str): The url of the video
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: View of the newly created video
    """
    alerts = models.Alerts()
    video_update = models.VideoUpdate(title=title, description=description, url=url)

    try:
        new_video = await crud.video.update(db=db, obj_in=video_update, id=video_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Video not found")
        response = RedirectResponse(url="/videos", status_code=status.HTTP_303_SEE_OTHER)
        response.headers["Method"] = "GET"
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    alerts.success.append("Video updated")
    return templates.TemplateResponse(
        "video/edit.html",
        {"request": request, "video": new_video, "current_user": current_user, "alerts": alerts},
    )


@router.get("/video/{video_id}/delete", response_class=HTMLResponse)
async def delete_video(
    video_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Video form.

    Args:
        video_id(str): The video id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new video
    """
    alerts = models.Alerts()
    try:
        await crud.video.remove(db=db, id=video_id)
        alerts.success.append("Video deleted")
    except crud.RecordNotFoundError:
        alerts.danger.append("Video not found")
    except crud.DeleteError:
        alerts.danger.append("Error deleting video")

    response = RedirectResponse(url="/videos", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response
