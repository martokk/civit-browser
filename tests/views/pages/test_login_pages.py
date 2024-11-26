from unittest.mock import Mock, patch

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from httpx import Cookies
from sqlmodel import Session

from app import crud


def test_login_page(client: TestClient) -> None:
    response = client.get("/login")
    assert response.status_code == 200


def test_handle_login_success(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test handling login
    """
    client.cookies = normal_user_cookies
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "root/home.html"  # type: ignore


def test_handle_login_failure(db_with_user: Session, client: TestClient) -> None:
    """
    Test handling login failure
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "login/login.html"  # type: ignore


def test_handle_login_exception(db_with_user: Session, client: TestClient) -> None:
    """
    Test handling login exception
    """
    response = client.post("/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 200
    assert response.context["error"].status_code == 401  # type: ignore
    assert response.context["error"].detail == "Incorrect username or password"  # type: ignore
    assert response.template.name == "login/login.html"  # type: ignore


def test_logout(db_with_user: Session, client: TestClient, normal_user_cookies: Cookies) -> None:
    """
    Test logout
    """
    # Test that the user is logged in
    client.cookies = normal_user_cookies
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "root/home.html"  # type: ignore

    # Logout
    response = client.get("/logout")
    assert response.status_code == 200

    # Test that the user is logged out
    assert response.template.name != "root/home.html"  # type: ignore


def test_register_page(client: TestClient) -> None:
    response = client.get("/register")
    assert response.status_code == 200


@patch("app.settings.USERS_OPEN_REGISTRATION", True)
async def test_handle_register_success(db_with_user: Session, client: TestClient) -> None:
    """
    Test handling register
    """
    data = {
        "username": "test_username",
        "password": "test_password",
        "password_confirmation": "test_password",
        "email": "test_email@gmail.com",
        "full_name": "test_full_name",
    }

    with patch("httpx.AsyncClient.post") as mocked_async_client:
        mocked_response = Mock()

        mocked_response.status_code = status.HTTP_201_CREATED
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/login.html"  # type: ignore
        assert mocked_async_client.call_args[1]["json"]["username"] == data["username"]
        assert mocked_async_client.call_args[1]["json"]["password"] == data["password"]
        assert mocked_async_client.call_args[1]["json"]["email"] == data["email"]
        assert mocked_async_client.call_args[1]["json"]["full_name"] == data["full_name"]


@patch("app.settings.USERS_OPEN_REGISTRATION", False)
async def test_handle_registration_closed(db_with_user: Session, client: TestClient) -> None:
    """
    Test registration closed
    """
    response = client.post("/register", data={})
    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "login/register.html"  # type: ignore
    assert response.context["alerts"].danger[0] == "Registration is closed"  # type: ignore


@patch("app.settings.USERS_OPEN_REGISTRATION", True)
async def test_handle_register_failure(db_with_user: Session, client: TestClient) -> None:
    """
    Test handling register
    """
    base_data = {
        "username": "test_username",
        "password": "test_password",
        "password_confirmation": "test_password",
        "email": "test_email@gmail.com",
        "full_name": "test_full_name",
    }

    with patch("httpx.AsyncClient.post") as mocked_async_client:
        mocked_response = Mock()

        # Test missing fields
        data = base_data.copy()
        data.pop("username")
        mocked_response.status_code = status.HTTP_200_OK
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/register.html"  # type: ignore
        assert response.context["alerts"].danger[0] == "Please fill out all fields"  # type: ignore

        # Test password mismatch
        data = base_data.copy()
        data["password_confirmation"] = "wrong_password"
        mocked_response.status_code = status.HTTP_200_OK
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/register.html"  # type: ignore
        assert response.context["alerts"].danger[0] == "Passwords do not match"  # type: ignore

        # Test invalid email
        data = base_data.copy()
        data["email"] = "invalid_email_address"
        mocked_response.status_code = status.HTTP_200_OK
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/register.html"  # type: ignore
        assert response.context["alerts"].danger[0] == "Invalid email"  # type: ignore

        # Test Username or email already exists
        mocked_response.status_code = status.HTTP_409_CONFLICT
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=base_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/register.html"  # type: ignore
        assert response.context["alerts"].danger[0] == "Username or email already exists"  # type: ignore

        # Test Invalid data
        mocked_response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=base_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/register.html"  # type: ignore
        assert response.context["alerts"].danger[0] == "Invalid data"  # type: ignore

        # Test Error registering user
        mocked_response.status_code = status.HTTP_400_BAD_REQUEST
        mocked_async_client.return_value = mocked_response
        response = client.post("/register", data=base_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.template.name == "login/register.html"  # type: ignore
        assert response.context["alerts"].danger[0] == "Error registering user"  # type: ignore


async def test_get_tokens_from_refresh_token(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test handling login with refresh token
    """
    normal_user_cookies.delete("access_token")
    client.cookies = normal_user_cookies
    response = client.get("/account")

    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "root/home.html"  # type: ignore
    assert response.url.path == "/"  # type: ignore


async def test_get_tokens_from_invalid_refresh_token(
    db_with_user: Session,  # pylint: disable=unused-argument
    client: TestClient,
    normal_user_cookies: Cookies,
) -> None:
    """
    Test invalid refresh token
    """
    normal_user_cookies.delete("access_token")
    normal_user_cookies.set("refresh_token", "invalid_refresh_token")
    client.cookies = normal_user_cookies
    response = client.get("/account")

    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "login/login.html"  # type: ignore
    assert response.url.path == "/login"  # type: ignore

    # Test invalid refresh token
    with patch(
        "app.core.security.get_tokens_from_refresh_token",
        side_effect=HTTPException(status_code=400),
    ):
        client.cookies = normal_user_cookies
        response = client.get("/account")
        assert response.status_code == status.HTTP_200_OK
        assert response.url.path == "/login"  # type: ignore
    # Test invalid refresh token
    with (
        patch(
            "app.core.security.decode_token",
            side_effect=HTTPException(status_code=400),
        ),
        patch(
            "app.core.security.get_tokens_from_refresh_token",
            side_effect=HTTPException(status_code=400),
        ),
    ):
        client.cookies = normal_user_cookies
        response = client.get("/account")
        assert response.status_code == status.HTTP_200_OK
        assert response.url.path == "/login"  # type: ignore

    # Test invalid refresh token
    with patch(
        "app.views.deps.get_current_user_or_raise",
        return_value=None,
    ):
        client.cookies.clear()
        response = client.get("/account")
        assert response.status_code == status.HTTP_200_OK
        assert response.url.path == "/login"  # type: ignore
