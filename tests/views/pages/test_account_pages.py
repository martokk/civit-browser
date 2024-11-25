from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlmodel import Session

from tests.mock_objects import MOCKED_IMAGES_1, MOCKED_IMAGESS


async def test_display_user_account(
    client: TestClient, db: Session, normal_user_cookies: Cookies
) -> None:
    """
    Test that a normal user can view their account.
    """
    client.cookies = normal_user_cookies
    response = client.get("/account")
    assert response.status_code == 200
    assert response.template.name == "user/view.html"  # type: ignore
    assert response.context["db_user"].username == "test_user"  # type: ignore


async def test_edit_user_account_page(
    client: TestClient, db: Session, normal_user_cookies: Cookies
) -> None:
    """
    Test that a normal user can view their account edit page.
    """
    client.cookies = normal_user_cookies
    response = client.get("/account/edit")
    assert response.status_code == 200
    assert response.template.name == "user/edit.html"  # type: ignore
    assert response.context["db_user"].username == "test_user"  # type: ignore


async def test_update_user_account(
    client: TestClient, db: Session, normal_user_cookies: Cookies
) -> None:
    """
    Test that a normal user can update their own account.
    """
    data: dict[str, Any] = {
        "full_name": "New Name",
        "email": "new_email@email.com",
        "is_active": False,
        "is_superuser": True,
    }
    client.cookies = normal_user_cookies
    response = client.post("/account/edit", data=data)
    assert response.status_code == 200
    assert response.template.name == "user/edit.html"  # type: ignore
    assert response.context["db_user"].username == "test_user"  # type: ignore
    assert response.context["db_user"].email == data["email"]  # type: ignore
    assert response.context["db_user"].full_name == data["full_name"]  # type: ignore
    assert response.context["db_user"].is_active == True  # type: ignore
    assert response.context["db_user"].is_superuser == False  # type: ignore


async def test_update_superuser_account(
    client: TestClient, db: Session, superuser_cookies: Cookies
) -> None:
    """
    Test that a superuser can update their own account.
    """
    data: dict[str, Any] = {
        "full_name": "New Name",
        "email": "new_email@email.com",
        "is_active": False,
        "is_superuser": True,
    }
    client.cookies = superuser_cookies
    response = client.post("/account/edit", data=data)
    assert response.status_code == 200
    assert response.template.name == "user/edit.html"  # type: ignore
    assert response.context["db_user"].email == data["email"]  # type: ignore
    assert response.context["db_user"].full_name == data["full_name"]  # type: ignore
    assert response.context["db_user"].is_active == data["is_active"]  # type: ignore
    assert response.context["db_user"].is_superuser == data["is_superuser"]  # type: ignore
