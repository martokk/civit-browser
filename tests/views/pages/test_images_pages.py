from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlmodel import Session

from app import crud, models, settings
from tests.mock_objects import MOCKED_IMAGES_1, MOCKED_IMAGESS


@pytest.fixture(name="images_1")
async def fixture_images_1(db_with_user: Session) -> models.Images:
    """
    Create an images for testing.
    """
    user = await crud.user.get(db=db_with_user, username="test_user")
    images_create = models.ImagesCreate(**MOCKED_IMAGES_1)
    return await crud.images.create_with_owner_id(
        db=db_with_user, obj_in=images_create, owner_id=user.id
    )


@pytest.fixture(name="imagess")
async def fixture_imagess(db_with_user: Session) -> list[models.Images]:
    """
    Create an images for testing.
    """
    # Create 1 as a superuser
    user = await crud.user.get(db=db_with_user, username=settings.FIRST_SUPERUSER_USERNAME)
    imagess = []
    images_create = models.ImagesCreate(**MOCKED_IMAGESS[0])
    imagess.append(
        await crud.images.create_with_owner_id(
            db=db_with_user, obj_in=images_create, owner_id=user.id
        )
    )

    # Create 2 as a normal user
    user = await crud.user.get(db=db_with_user, username="test_user")
    for mocked_images in [MOCKED_IMAGESS[1], MOCKED_IMAGESS[2]]:
        images_create = models.ImagesCreate(**mocked_images)
        imagess.append(
            await crud.images.create_with_owner_id(
                db=db_with_user, obj_in=images_create, owner_id=user.id
            )
        )
    return imagess


def test_create_images_page(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that the create images page is returned.
    """
    client.cookies = normal_user_cookies
    response = client.get("/imagess/create")
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/create.html"  # type: ignore


def test_handle_create_images(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can create a new images.
    """
    client.cookies = normal_user_cookies
    response = client.post(
        "/imagess/create",
        data=MOCKED_IMAGES_1,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/list.html"  # type: ignore


@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
def test_create_duplicate_images(
    db_with_user: Session,  # pylint: disable=unused-argument
    images_1: models.Images,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:  # pytest:
    """
    Test a duplicate images cannot be created.
    """
    # Try to create a duplicate images
    with pytest.raises(Exception):
        response = client.post(
            "/imagess/create",
            data=MOCKED_IMAGES_1,
        )
    # assert response.status_code == status.HTTP_200_OK
    # assert response.template.name == "images/create.html"  # type: ignore
    # assert response.context["alerts"].danger[0] == "Images already exists"  # type: ignore


def test_read_images(
    db_with_user: Session,  # pylint: disable=unused-argument
    images_1: models.Images,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can read an images.
    """
    # Read the images
    response = client.get(
        f"/images/{images_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/view.html"  # type: ignore


def test_get_images_not_found(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a images not found error is returned.
    """
    client.cookies = normal_user_cookies

    # Read the images
    response = client.get("/images/8675309")
    assert response.status_code == status.HTTP_200_OK
    assert response.url.path == "/imagess"


def test_get_images_forbidden(
    db_with_user: Session,  # pylint: disable=unused-argument
    images_1: models.Images,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a forbidden error is returned when a user tries to read an images
    """
    client.cookies = normal_user_cookies

    # Read the images
    response = client.get(
        f"/images/{images_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/view.html"  # type: ignore

    # Logout
    response = client.get(
        "/logout",
    )
    assert response.status_code == status.HTTP_200_OK

    # Attempt Read the images
    response = client.get(
        f"/images/{images_1.id}",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.url.path == "/login"  # type: ignore


def test_normal_user_get_all_imagess(
    db_with_user: Session,  # pylint: disable=unused-argument
    imagess: list[models.Images],  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
    superuser_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a normal user can get all their own imagess.
    """

    # List all imagess as normal user
    client.cookies = normal_user_cookies
    response = client.get(
        "/imagess",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/list.html"  # type: ignore

    # Assert only 2 imagess are returned (not the superuser's images)
    assert len(response.context["imagess"]) == 2  # type: ignore


def test_edit_images_page(
    db_with_user: Session,  # pylint: disable=unused-argument
    images_1: models.Images,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that the edit images page is returned.
    """
    client.cookies = normal_user_cookies
    response = client.get(
        f"/images/{images_1.id}/edit",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/edit.html"  # type: ignore

    # Test invalid images id
    response = client.get(
        f"/images/invalid_user_id/edit",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_302_FOUND
    assert response.context["alerts"].danger[0] == "Images not found"  # type: ignore
    assert response.url.path == "/imagess"


def test_update_images(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    images_1: models.Images,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can update an images.
    """
    client.cookies = normal_user_cookies

    # Update the images
    response = client.post(
        f"/images/{images_1.id}/edit",  # type: ignore
        data=MOCKED_IMAGESS[1],
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/edit.html"  # type: ignore

    # View the images
    response = client.get(
        f"/images/{images_1.id}",  # type: ignore
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/view.html"  # type: ignore
    assert response.context["images"].title == MOCKED_IMAGESS[1]["title"]  # type: ignore
    assert response.context["images"].description == MOCKED_IMAGESS[1]["description"]  # type: ignore
    assert response.context["images"].url == MOCKED_IMAGESS[1]["url"]  # type: ignore

    # Test invalid images id
    response = client.post(
        f"/images/invalid_user_id/edit",  # type: ignore
        data=MOCKED_IMAGESS[1],
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.context["alerts"].danger[0] == "Images not found"  # type: ignore
    assert response.url.path == "/imagess"


def test_delete_images(
    db_with_user: Session,  # pylint: disable=unused-argument
    images_1: models.Images,
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test that a user can delete an images.
    """
    client.cookies = normal_user_cookies

    # Delete the images
    response = client.get(
        f"/images/{images_1.id}/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.url.path == "/imagess"

    # View the images
    response = client.get(
        f"/images/{images_1.id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.context["alerts"].danger == ["Images not found"]  # type: ignore

    # Test invalid images id
    response = client.get(
        f"/images/invalid_user_id/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
    assert response.context["alerts"].danger[0] == "Images not found"  # type: ignore
    assert response.url.path == "/imagess"

    # Test DeleteError
    with patch("app.crud.images.remove", side_effect=crud.DeleteError):
        response = client.get(
            f"/images/123/delete",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.history[0].status_code == status.HTTP_303_SEE_OTHER
        assert response.context["alerts"].danger[0] == "Error deleting images"  # type: ignore


def test_list_all_imagess(
    db_with_user: Session,  # pylint: disable=unused-argument
    imagess: list[models.Images],  # pylint: disable=unused-argument
    client: TestClient,
    superuser_cookies: Cookies,
) -> None:  # sourcery skip: extract-duplicate-method
    """
    Test that a superuser can get all imagess.
    """

    # List all imagess as superuser
    client.cookies = superuser_cookies
    response = client.get(
        "/imagess/all",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "images/list.html"  # type: ignore

    # Assert all 3 imagess are returned
    assert len(response.context["imagess"]) == 3  # type: ignore
