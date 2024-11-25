from fastapi.testclient import TestClient
from sqlmodel import Session

from app import settings
from tests.mock_objects import MOCKED_IMAGES_1, MOCKED_IMAGESS


def test_create_images(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can create a new images.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 201
    images = response.json()
    assert images["title"] == MOCKED_IMAGES_1["title"]
    assert images["description"] == MOCKED_IMAGES_1["description"]
    assert images["url"] == MOCKED_IMAGES_1["url"]
    assert images["owner_id"] is not None
    assert images["id"] is not None


def test_create_duplicate_images(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test a duplicate images cannot be created.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 201

    # Try to create a duplicate images
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 200
    duplicate = response.json()
    assert duplicate["detail"] == "Images already exists"


def test_read_images(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can read an images.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 201
    created_images = response.json()

    # Read Images
    response = client.get(
        f"{settings.API_V1_PREFIX}/images/{created_images['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    read_images = response.json()

    assert read_images["title"] == MOCKED_IMAGES_1["title"]
    assert read_images["description"] == MOCKED_IMAGES_1["description"]
    assert read_images["url"] == MOCKED_IMAGES_1["url"]
    assert read_images["owner_id"] is not None
    assert read_images["id"] is not None


def test_get_images_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a images not found error is returned.
    """
    response = client.get(
        f"{settings.API_V1_PREFIX}/images/1",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Images not found"


def test_get_images_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.get(
        f"{settings.API_V1_PREFIX}/images/5kwf8hFn",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_superuser_get_all_imagess(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    """
    Test that a superuser can get all imagess.
    """

    # Create 3 imagess
    for images in MOCKED_IMAGESS:
        response = client.post(
            f"{settings.API_V1_PREFIX}/images/",
            headers=superuser_token_headers,
            json=images,
        )
        assert response.status_code == 201

    # Get all imagess as superuser
    response = client.get(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    imagess = response.json()
    assert len(imagess) == 3


def test_normal_user_get_all_imagess(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
) -> None:
    """
    Test that a normal user can get all their own imagess.
    """
    # Create 2 imagess as normal user
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=normal_user_token_headers,
        json=MOCKED_IMAGESS[0],
    )
    assert response.status_code == 201
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=normal_user_token_headers,
        json=MOCKED_IMAGESS[1],
    )
    assert response.status_code == 201

    # Create 1 images as super user
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGESS[2],
    )
    assert response.status_code == 201

    # Get all imagess as normal user
    response = client.get(
        f"{settings.API_V1_PREFIX}/images/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    imagess = response.json()
    assert len(imagess) == 2


def test_update_images(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can update an images.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 201
    created_images = response.json()

    # Update Images
    update_data = MOCKED_IMAGES_1.copy()
    update_data["title"] = "Updated Title"
    response = client.patch(
        f"{settings.API_V1_PREFIX}/images/{created_images['id']}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_images = response.json()
    assert updated_images["title"] == update_data["title"]

    # Update wrong images
    response = client.patch(
        f"{settings.API_V1_PREFIX}/images/99999",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 404


def test_update_images_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.patch(
        f"{settings.API_V1_PREFIX}/images/5kwf8hFn",
        headers=normal_user_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_images(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    """
    Test that a superuser can delete an images.
    """
    response = client.post(
        f"{settings.API_V1_PREFIX}/images/",
        headers=superuser_token_headers,
        json=MOCKED_IMAGES_1,
    )
    assert response.status_code == 201
    created_images = response.json()

    # Delete Images
    response = client.delete(
        f"{settings.API_V1_PREFIX}/images/{created_images['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204

    # Delete wrong images
    response = client.delete(
        f"{settings.API_V1_PREFIX}/images/99999",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_delete_images_forbidden(
    db_with_user: Session, client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a forbidden error is returned.
    """
    response = client.delete(
        f"{settings.API_V1_PREFIX}/images/5kwf8hFn",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
