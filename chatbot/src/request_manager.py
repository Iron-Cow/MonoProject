from typing import Any

import requests
from config import Config


class RequestManager:
    def __init__(self, config: Config):
        self.api_host = config.API_HOST
        self.CHAT_BOT_API_KEY = config.CHAT_BOT_API_KEY
        self.__admin_login = config.API_ADMIN_USERNAME
        self.__admin_password = config.API_ADMIN_PASSWORD
        self.__refresh_token = None

    def __get_auth_token(self, initial: bool = False) -> str:
        if initial:
            endpoint = "/account/token/"
            resp = requests.post(
                f"{self.api_host}{endpoint}",
                json={"tg_id": self.__admin_login, "password": self.__admin_password},
                headers={"content-type": "application/json"},
            )
            if resp.status_code != 200:
                data = f"code - {resp.status_code}, text - {resp.text}"
                raise PermissionError(f"Failed to get initial auth tokens. {data}")
            try:
                access_token, refresh_token = resp.json().get(
                    "access"
                ), resp.json().get("refresh")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid .json() parsing result from {resp.text}")
            self.__refresh_token = refresh_token
            return access_token
        else:
            endpoint = "/account/token-refresh/"
            resp = requests.post(
                f"{self.api_host}{endpoint}",
                json={"refresh": self.__refresh_token},
                headers={"content-type": "application/json"},
            )
            if resp.status_code != 200:
                return self.__get_auth_token(True)
            try:
                access_token = resp.json().get("access")
                return access_token
            except (ValueError, TypeError):
                raise ValueError(f"Invalid .json() parsing result from {resp.text}")

    def create_default_headers(self) -> dict:
        is_initial = False
        if self.__refresh_token is None:
            is_initial = True
        auth_token = self.__get_auth_token(is_initial)
        return {
            "Authorization": f"Bearer {auth_token}",
            "content-type": "application/json",
        }

    def get(self, endpoint: str) -> requests.Response:
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        headers = self.create_default_headers()
        resp = requests.get(f"{self.api_host}{endpoint}", headers=headers)
        return resp

    def post(
        self, endpoint: str, body: dict[str, Any] | None = None
    ) -> requests.Response:
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        headers = self.create_default_headers()
        resp = requests.post(f"{self.api_host}{endpoint}", json=body, headers=headers)
        return resp

    def patch(
        self, endpoint: str, body: dict[str, Any] | None = None
    ) -> requests.Response:
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        headers = self.create_default_headers()
        resp = requests.patch(f"{self.api_host}{endpoint}", json=body, headers=headers)
        return resp

    def delete(
        self, endpoint: str, body: dict[str, Any] | None = None
    ) -> requests.Response:
        if endpoint[0] != "/":
            endpoint = "/" + endpoint

        headers = self.create_default_headers()
        resp = requests.delete(f"{self.api_host}{endpoint}", json=body, headers=headers)
        return resp
