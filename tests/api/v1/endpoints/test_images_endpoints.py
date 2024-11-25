from fastapi.testclient import TestClient
from sqlmodel import Session

from app import settings
from tests.mock_objects import MOCKED_VIDEO_1, MOCKED_VIDEOS


def test_create_video(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can create a new video.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 201
    video = response.json()
    assert video["title"] == MOCKED_VIDEO_1["title"]
    assert video["description"] == MOCKED_VIDEO_1["description"]
    assert video["url"] == MOCKED_VIDEO_1["url"]
    assert video["owner_id"] is not None
    assert video["id"] is not None


def test_create_duplicate_video(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test a duplicate video cannot be created.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 201

    # Try to create a duplicate video
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 200
    duplicate = response.json()
    assert duplicate["detail"] == "Video already exists"


def test_read_video(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can read an video.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 201
    created_video = response.json()

    # Read Video
    response = client.get(
        f"{settings.API_V1_PREFIX}/video/{created_video['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    read_video = response.json()

    assert read_video["title"] == MOCKED_VIDEO_1["title"]
    assert read_video["description"] == MOCKED_VIDEO_1["description"]
    assert read_video["url"] == MOCKED_VIDEO_1["url"]
    assert read_video["owner_id"] is not None
    assert read_video["id"] is not None


def test_get_video_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a video not found error is returned.
    """
    response = client.get(
        f"{settings.API_V1_PREFIX}/video/1",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Video not found"


def test_get_video_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.get(
        f"{settings.API_V1_PREFIX}/video/5kwf8hFn",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_superuser_get_all_videos(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    """
    Test that a superuser can get all videos.
    """

    # Create 3 videos
    for video in MOCKED_VIDEOS:
        response = client.post(
            f"{settings.API_V1_PREFIX}/video/",
            headers=superuser_token_headers,
            json=video,
        )
        assert response.status_code == 201

    # Get all videos as superuser
    response = client.get(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    videos = response.json()
    assert len(videos) == 3


def test_normal_user_get_all_videos(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
) -> None:
    """
    Test that a normal user can get all their own videos.
    """
    # Create 2 videos as normal user
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=normal_user_token_headers,
        json=MOCKED_VIDEOS[0],
    )
    assert response.status_code == 201
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=normal_user_token_headers,
        json=MOCKED_VIDEOS[1],
    )
    assert response.status_code == 201

    # Create 1 video as super user
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEOS[2],
    )
    assert response.status_code == 201

    # Get all videos as normal user
    response = client.get(
        f"{settings.API_V1_PREFIX}/video/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    videos = response.json()
    assert len(videos) == 2


def test_update_video(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can update an video.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 201
    created_video = response.json()

    # Update Video
    update_data = MOCKED_VIDEO_1.copy()
    update_data["title"] = "Updated Title"
    response = client.patch(
        f"{settings.API_V1_PREFIX}/video/{created_video['id']}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_video = response.json()
    assert updated_video["title"] == update_data["title"]

    # Update wrong video
    response = client.patch(
        f"{settings.API_V1_PREFIX}/video/99999",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 404


def test_update_video_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.patch(
        f"{settings.API_V1_PREFIX}/video/5kwf8hFn",
        headers=normal_user_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_video(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can delete an video.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/video/",
        headers=superuser_token_headers,
        json=MOCKED_VIDEO_1,
    )
    assert response.status_code == 201
    created_video = response.json()

    # Delete Video
    response = client.delete(
        f"{settings.API_V1_PREFIX}/video/{created_video['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204

    # Delete wrong video
    response = client.delete(
        f"{settings.API_V1_PREFIX}/video/99999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_delete_video_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.delete(
        f"{settings.API_V1_PREFIX}/video/5kwf8hFn",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
