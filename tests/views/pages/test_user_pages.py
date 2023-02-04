from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlmodel import Session


def test_display_user_account_page(
    client: TestClient, db: Session, superuser_cookies: Cookies
) -> None:
    """
    Test that superusers can view a users account page.
    """
    response = client.get("/user/test_user", cookies=superuser_cookies)
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "user/view.html"  # type: ignore
    assert response.context["db_user"].username == "test_user"  # type: ignore

    # Test user not found
    response = client.get("/user/wrong_username", cookies=superuser_cookies)
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "base/base.html"  # type: ignore
    assert response.context["alerts"].danger == ["User not found"]  # type: ignore


def test_edit_user_account_page(
    client: TestClient, db: Session, superuser_cookies: Cookies
) -> None:
    """
    Test that superusers can edit a users account page.
    """
    response = client.get("/user/test_user/edit", cookies=superuser_cookies)
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "user/edit.html"  # type: ignore
    assert response.context["db_user"].username == "test_user"  # type: ignore

    # Test user not found
    response = client.get("/user/wrong_username/edit", cookies=superuser_cookies)
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "item/list.html"  # type: ignore
    assert response.context["alerts"].danger == ["User not found"]  # type: ignore


def test_update_user_account(client: TestClient, db: Session, superuser_cookies: Cookies) -> None:
    """
    Test that superusers can update a users account.
    """
    data: dict[str, Any] = {
        "full_name": "New Name",
        "email": "new_email@gmail.com",
        "is_active": False,
        "is_superuser": True,
    }
    response = client.post("/user/test_user/edit", cookies=superuser_cookies, data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "user/edit.html"  # type: ignore
    assert response.context["db_user"].username == "test_user"  # type: ignore
    assert response.context["db_user"].email == data["email"]  # type: ignore
    assert response.context["db_user"].full_name == data["full_name"]  # type: ignore
    assert response.context["db_user"].is_active == data["is_active"]  # type: ignore
    assert response.context["db_user"].is_superuser == data["is_superuser"]  # type: ignore

    # Test user not found & redirect
    response = client.post("/user/wrong_username/edit", cookies=superuser_cookies, data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.history[0].status_code == status.HTTP_302_FOUND
    assert response.context["alerts"].danger == ["User not found"]  # type: ignore
    assert response.url == "http://testserver/"