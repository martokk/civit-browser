from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app import crud, models
from tests.mock_objects import MOCKED_VIDEO_1, MOCKED_VIDEOS


async def get_mocked_video(db: Session) -> models.Video:
    """
    Create a mocked video.
    """
    # Create an video with an owner
    owner = await crud.user.get(db=db, username="test_user")
    video_create = models.VideoCreate(**MOCKED_VIDEO_1)

    return await crud.video.create_with_owner_id(db=db, obj_in=video_create, owner_id=owner.id)


async def test_create_video(db_with_user: Session) -> None:
    """
    Test creating a new video with an owner.
    """
    created_video = await get_mocked_video(db=db_with_user)

    # Check the video was created
    assert created_video.title == MOCKED_VIDEO_1["title"]
    assert created_video.description == MOCKED_VIDEO_1["description"]
    assert created_video.owner_id is not None


async def test_get_video(db_with_user: Session) -> None:
    """
    Test getting an video by id.
    """
    created_video = await get_mocked_video(db=db_with_user)

    # Get the video
    db_video = await crud.video.get(db=db_with_user, id=created_video.id)
    assert db_video
    assert db_video.id == created_video.id
    assert db_video.title == created_video.title
    assert db_video.description == created_video.description
    assert db_video.owner_id == created_video.owner_id


async def test_update_video(db_with_user: Session) -> None:
    """
    Test updating an video.
    """
    created_video = await get_mocked_video(db=db_with_user)

    # Update the video
    db_video = await crud.video.get(db=db_with_user, id=created_video.id)
    db_video_update = models.VideoUpdate(description="New Description")
    updated_video = await crud.video.update(
        db=db_with_user, id=created_video.id, obj_in=db_video_update
    )
    assert db_video.id == updated_video.id
    assert db_video.title == updated_video.title
    assert updated_video.description == "New Description"
    assert db_video.owner_id == updated_video.owner_id


async def test_update_video_without_filter(db_with_user: Session) -> None:
    """
    Test updating an video without a filter.
    """
    created_video = await get_mocked_video(db=db_with_user)

    # Update the video (without a filter)
    await crud.video.get(db=db_with_user, id=created_video.id)
    db_video_update = models.VideoUpdate(description="New Description")
    with pytest.raises(ValueError):
        await crud.video.update(db=db_with_user, obj_in=db_video_update)


async def test_delete_video(db_with_user: Session) -> None:
    """
    Test deleting an video.
    """
    created_video = await get_mocked_video(db=db_with_user)

    # Delete the video
    await crud.video.remove(db=db_with_user, id=created_video.id)
    with pytest.raises(crud.RecordNotFoundError):
        await crud.video.get(db=db_with_user, id=created_video.id)


async def test_delete_video_delete_error(db_with_user: Session, mocker: MagicMock) -> None:
    """
    Test deleting an video with a delete error.
    """
    mocker.patch("app.crud.video.get", return_value=None)
    with pytest.raises(crud.DeleteError):
        await crud.video.remove(db=db_with_user, id="00000001")


async def test_get_all_videos(db_with_user: Session) -> None:
    """
    Test getting all videos.
    """
    # Create some videos
    for i, video in enumerate(MOCKED_VIDEOS):
        video_create = models.VideoCreate(**video)
        await crud.video.create_with_owner_id(
            db=db_with_user, obj_in=video_create, owner_id=f"0000000{i}"
        )

    # Get all videos
    videos = await crud.video.get_all(db=db_with_user)
    assert len(videos) == len(MOCKED_VIDEOS)
