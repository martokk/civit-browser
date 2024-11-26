from fastapi import Request
from sqlmodel import SQLModel


class Alerts(SQLModel):
    """
    Alerts object. Based on Bootstrap alerts.
    """

    primary: list[str] = []
    secondary: list[str] = []
    success: list[str] = []
    danger: list[str] = []
    warning: list[str] = []
    info: list[str] = []
    light: list[str] = []
    dark: list[str] = []

    @classmethod
    def from_cookies(cls, cookies: dict[str, str]) -> "Alerts":
        """
        Get alerts from cookies.

        Args:
            cookies(dict): The cookies dict

        Returns:
            Alerts: The alerts object
        """
        for key, value in cookies.items():
            if key == "alerts":
                result = cls.parse_raw(value)
                if isinstance(result, cls):
                    return result
                raise ValueError("Invalid alert data")
        return cls()

    @classmethod
    def from_request(cls, request: Request) -> "Alerts":
        """
        Get alerts from request.

        Args:
            request(Request): The request object

        Returns:
            Alerts: The alerts object
        """
        return cls.from_cookies(cookies=request.cookies)
