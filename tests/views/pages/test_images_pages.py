from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlmodel import Session

from app import crud, models, settings
from tests.mock_objects import MOCKED_VIDEO_1, MOCKED_VIDEOS


@pytest.fixture(name="video_1")
async def fixture_video_1(db_with_user: Session) -> models.Video:
    """
    Create an video for testing.
    """
    user = await crud.user.get(db=db_with_user, username="test_user")
    video_create = models.VideoCreate(**MOCKED_VIDEO_1)
    return await crud.video.create_with_owner_id(
        db=db_with_user, obj_in=video_create, owner_id=user.id
    )


@pytest.fixture(name="videos")
async def fixture_videos(db_with_user: Session) -> list[models.Video]:
    """
    Create an video for testing.
    """
    # Create 1 as a superuser
    user = await crud.user.get(db=db_with_user, username=settings.FIRST_SUPERUSER_USERNAME)
    videos = []
    video_create = models.VideoCreate(**MOCKED_VIDEOS[0])
    videos.append(
        await crud.video.create_with_owner_id(
            db=db_with_user, obj_in=video_create, owner_id=user.id
        )
    )

    # Create 2 as a normal user
    user = await crud.user.get(db=db_with_user, username="test_user")
    for mocked_video in [MOCKED_VIDEOS[1], MOCKED_VIDEOS[2]]:
        video_create = models.VideoCreate(**mocked_video)
        videos.append(
            await crud.video.create_with_owner_id(
                db=db_with_user, obj_in=video_create, owner_id=user.id
            )
        )
    return videos


def test_create_video_page(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that the create video page is returned.
    """
    client.cookies = normal_user_cookies
    response = client.get("/videos/create")
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/create.html"  # type: ignore


def test_handle_create_video(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can create a new video.
    """
    client.cookies = normal_user_cookies
    response = client.post(
        "/videos/create",
        data=MOCKED_VIDEO_1,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/list.html"  # type: ignore


@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_create_duplicate_video(
    db_with_user: Session,  # pylint: disable=unused-argument
    video_1: models.Video,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:  # pytest:
    """
    Test a duplicate video cannot be created.
    """
    # Try to create a duplicate video
    with pytest.raises(Exception):
        response = client.post(
            "/videos/create",
            data=MOCKED_VIDEO_1,
        )
    # assert response.status_code == status.HTTP_200_OK
    # assert response.template.name == "video/create.html"  # type: ignore
    # assert response.context["alerts"].danger[0] == "Video already exists"  # type: ignore


def test_read_video(
    db_with_user: Session,  # pylint: disable=unused-argument
    video_1: models.Video,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can read an video.
    """
    # Read the video
    response = client.get(
        f"/video/{video_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/view.html"  # type: ignore


def test_get_video_not_found(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a video not found error is returned.
    """
    client.cookies = normal_user_cookies

    # Read the video
    response = client.get("/video/8675309")
    assert response.status_code == status.HTTP_200_OK
    assert response.url.path == "/videos"


def test_get_video_forbidden(
    db_with_user: Session,  # pylint: disable=unused-argument
    video_1: models.Video,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a forbidden error is returned when a user tries to read an video
    """
    client.cookies = normal_user_cookies

    # Read the video
    response = client.get(
        f"/video/{video_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/view.html"  # type: ignore

    # Logout
    response = client.get(
        "/logout",
    )
    assert response.status_code == status.HTTP_200_OK

    # Attempt Read the video
    response = client.get(
        f"/video/{video_1.id}",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.url.path == "/login"  # type: ignore


def test_normal_user_get_all_videos(
    db_with_user: Session,  # pylint: disable=unused-argument
    videos: list[models.Video],  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
    superuser_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a normal user can get all their own videos.
    """

    # List all videos as normal user
    client.cookies = normal_user_cookies
    response = client.get(
        "/videos",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/list.html"  # type: ignore

    # Assert only 2 videos are returned (not the superuser's video)
    assert len(response.context["videos"]) == 2  # type: ignore


def test_edit_video_page(
    db_with_user: Session,  # pylint: disable=unused-argument
    video_1: models.Video,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that the edit video page is returned.
    """
    client.cookies = normal_user_cookies
    response = client.get(
        f"/video/{video_1.id}/edit",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/edit.html"  # type: ignore

    # Test invalid video id
    response = client.get(
        f"/video/invalid_user_id/edit",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_302_FOUND
    assert response.context["alerts"].danger[0] == "Video not found"  # type: ignore
    assert response.url.path == "/videos"


def test_update_video(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    video_1: models.Video,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can update an video.
    """
    client.cookies = normal_user_cookies

    # Update the video
    response = client.post(
        f"/video/{video_1.id}/edit",  # type: ignore
        data=MOCKED_VIDEOS[1],
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/edit.html"  # type: ignore

    # View the video
    response = client.get(
        f"/video/{video_1.id}",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/view.html"  # type: ignore
    assert response.context["video"].title == MOCKED_VIDEOS[1]["title"]  # type: ignore
    assert response.context["video"].description == MOCKED_VIDEOS[1]["description"]  # type: ignore
    assert response.context["video"].url == MOCKED_VIDEOS[1]["url"]  # type: ignore

    # Test invalid video id
    response = client.post(
        f"/video/invalid_user_id/edit",  # type: ignore
        data=MOCKED_VIDEOS[1],
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.context["alerts"].danger[0] == "Video not found"  # type: ignore
    assert response.url.path == "/videos"


def test_delete_video(
    db_with_user: Session,  # pylint: disable=unused-argument
    video_1: models.Video,
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can delete an video.
    """
    client.cookies = normal_user_cookies

    # Delete the video
    response = client.get(
        f"/video/{video_1.id}/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.url.path == "/videos"

    # View the video
    response = client.get(
        f"/video/{video_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.context["alerts"].danger == ["Video not found"]  # type: ignore

    # Test invalid video id
    response = client.get(
        f"/video/invalid_user_id/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.context["alerts"].danger[0] == "Video not found"  # type: ignore
    assert response.url.path == "/videos"

    # Test DeleteError
    with patch("app.crud.video.remove", side_effect=crud.DeleteError):
        response = client.get(
            f"/video/123/delete",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
        assert response.context["alerts"].danger[0] == "Error deleting video"  # type: ignore


def test_list_all_videos(
    db_with_user: Session,  # pylint: disable=unused-argument
    videos: list[models.Video],  # pylint: disable=unused-argument
    client: TestClient,
    superuser_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a superuser can get all videos.
    """

    # List all videos as superuser
    client.cookies = superuser_cookies
    response = client.get(
        "/videos/all",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "video/list.html"  # type: ignore

    # Assert all 3 videos are returned
    assert len(response.context["videos"]) == 3  # type: ignore
