from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app import crud, models
from tests.mock_objects import MOCKED_IMAGES_1, MOCKED_IMAGESS


async def get_mocked_images(db: Session) -> models.Images:
    """
    Create a mocked images.
    """
    # Create an images with an owner
    owner = await crud.user.get(db=db, username="test_user")
    images_create = models.ImagesCreate(**MOCKED_IMAGES_1)

    return await crud.images.create_with_owner_id(db=db, obj_in=images_create, owner_id=owner.id)


async def test_create_images(db_with_user: Session) -> None:
    """
    Test creating a new images with an owner.
    """
    created_images = await get_mocked_images(db=db_with_user)

    # Check the images was created
    assert created_images.title == MOCKED_IMAGES_1["title"]
    assert created_images.description == MOCKED_IMAGES_1["description"]
    assert created_images.owner_id is not None


async def test_get_images(db_with_user: Session) -> None:
    """
    Test getting an images by id.
    """
    created_images = await get_mocked_images(db=db_with_user)

    # Get the images
    db_images = await crud.images.get(db=db_with_user, id=created_images.id)
    assert db_images
    assert db_images.id == created_images.id
    assert db_images.title == created_images.title
    assert db_images.description == created_images.description
    assert db_images.owner_id == created_images.owner_id


async def test_update_images(db_with_user: Session) -> None:
    """
    Test updating an images.
    """
    created_images = await get_mocked_images(db=db_with_user)

    # Update the images
    db_images = await crud.images.get(db=db_with_user, id=created_images.id)
    db_images_update = models.ImagesUpdate(description="New Description")
    updated_images = await crud.images.update(
        db=db_with_user, id=created_images.id, obj_in=db_images_update
    )
    assert db_images.id == updated_images.id
    assert db_images.title == updated_images.title
    assert updated_images.description == "New Description"
    assert db_images.owner_id == updated_images.owner_id


async def test_update_images_without_filter(db_with_user: Session) -> None:
    """
    Test updating an images without a filter.
    """
    created_images = await get_mocked_images(db=db_with_user)

    # Update the images (without a filter)
    await crud.images.get(db=db_with_user, id=created_images.id)
    db_images_update = models.ImagesUpdate(description="New Description")
    with pytest.raises(ValueError):
        await crud.images.update(db=db_with_user, obj_in=db_images_update)


async def test_delete_images(db_with_user: Session) -> None:
    """
    Test deleting an images.
    """
    created_images = await get_mocked_images(db=db_with_user)

    # Delete the images
    await crud.images.remove(db=db_with_user, id=created_images.id)
    with pytest.raises(crud.RecordNotFoundError):
        await crud.images.get(db=db_with_user, id=created_images.id)


async def test_delete_images_delete_error(db_with_user: Session, mocker: MagicMock) -> None:
    """
    Test deleting an images with a delete error.
    """
    mocker.patch("app.crud.images.get", return_value=None)
    with pytest.raises(crud.DeleteError):
        await crud.images.remove(db=db_with_user, id="00000001")


async def test_get_all_imagess(db_with_user: Session) -> None:
    """
    Test getting all imagess.
    """
    # Create some imagess
    for i, images in enumerate(MOCKED_IMAGESS):
        images_create = models.ImagesCreate(**images)
        await crud.images.create_with_owner_id(
            db=db_with_user, obj_in=images_create, owner_id=f"0000000{i}"
        )

    # Get all imagess
    imagess = await crud.images.get_all(db=db_with_user)
    assert len(imagess) == len(MOCKED_IMAGESS)
