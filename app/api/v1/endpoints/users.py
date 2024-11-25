from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from pydantic.networks import EmailStr
from sqlmodel import Session

from app import crud, models, settings
from app.api import deps
from app.core import notify, security

router = APIRouter()

router = APIRouter()
ModelClass = models.User
ModelReadClass = models.UserRead
ModelCreateClass = models.UserCreate
ModelUpdateClass = models.UserUpdate
model_crud = crud.user


@router.get("/", response_model=list[models.UserRead])
async def get_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> list[ModelClass]:
    """
    Retrieve users.

    Args:
        db (Session): database session.
        skip (int): Number of users to skip. Defaults to 0.
        limit (int): Number of users to return. Defaults to 100.
        _ (models.User): Current active user.

    Returns:
        list[ModelClass]: List of objects.
    """
    return await crud.user.get_multi(db=db, skip=skip, limit=limit)


@router.get("/me", response_model=models.UserRead)
async def get_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.User:
    """
    Get current user.

    Args:
        current_user (models.User): Current active user.

    Returns:
        models.User: Current user.
    """
    return current_user


@router.get("/{id}", response_model=models.UserRead)
async def get_by_id(
    id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> models.User:
    """
    Get user by id.

    Args:
        id (str): id of the user.
        db (Session): database session.
        current_user (Any): authenticated user.

    Returns:
        ModelClass: Retrieved object.

    Raises:
        HTTPException: if object not found.
    """
    is_superuser = crud.user.is_superuser(user_=current_user)

    user = await crud.user.get_or_none(db, id=id)
    if not user:
        if not is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not is_superuser and user != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return user


@router.post("/", response_model=models.UserRead)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: models.UserCreateWithPassword,
    _: models.User = Depends(deps.get_current_active_superuser),
    background_tasks: BackgroundTasks,
) -> models.User:
    """
    Create new user.

    Args:
        db (Session): database session.
        user_in (models.UserCreate): user data.
        _ (models.User): Current active user.
        background_tasks (BackgroundTasks): background tasks.

    Returns:
        models.User: Created user.

    Raises:
        HTTPException: if user already exists.
    """
    # Creates user
    try:
        user = await crud.user.create_with_password(db, obj_in=user_in)
    except crud.RecordAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this username/email already exists in the system.",
        ) from e

    # Sends email
    if settings.EMAILS_ENABLED and user_in.email:
        background_tasks.add_task(
            notify.send_new_account_email,
            email_to=user_in.email,
            username=user_in.username,
            password=user_in.password,
        )
    return user


@router.patch("/{user_id}", response_model=models.UserRead)
async def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: models.UserUpdate,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> models.User:
    """
    Update a user.

    Args:
        db (Session): database session.
        user_id (str): id of the user.
        user_in (models.UserUpdate): user data.
        _ (models.User): Current active user.

    Returns:
        models.UserRead: Updated user.
    """
    return await crud.user.update(db, id=user_id, obj_in=user_in)


@router.put("/me", response_model=models.UserRead)
async def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.User:
    """
    Update own user.

    Args:
        db (Session): database session.
        password (str): password.
        full_name (str): full name.
        email (EmailStr): email.
        current_user (models.User): Current active user.

    Returns:
        models.User: Updated user.
    """
    user_in = models.UserUpdate(**current_user.dict())
    if password is not None:
        user_in.hashed_password = security.get_password_hash(password=password)
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = await crud.user.update(db, id=current_user.id, obj_in=user_in)
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    *,
    db: Session = Depends(deps.get_db),
    id: str,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> None:
    """
    Delete an user. Only superusers can delete imagess.

    Args:
        id (str): ID of the user to delete.
        db (Session): database session.
        _ (models.User): Current active superuser.

    Returns:
        None

    Raises:
        HTTPException: if user not found.
    """
    try:
        return await model_crud.remove(id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found") from exc
