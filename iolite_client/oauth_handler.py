import json
import logging
import os
import time
from typing import Optional
from urllib.parse import urlencode

import aiohttp
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://remote.iolite.de"
CLIENT_ID = "deuwo_mia_app"


class OAuthHandlerHelper:
    @staticmethod
    def get_access_token_query(code: str, name: str) -> str:
        return urlencode(
            {
                "client_id": CLIENT_ID,
                "grant_type": "authorization_code",
                "code": code,
                "name": name,
            }
        )

    @staticmethod
    def get_new_access_token_query(refresh_token: str) -> str:
        return urlencode(
            {
                "client_id": CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

    @staticmethod
    def get_sid_query(access_token: str) -> str:
        return urlencode(
            {
                "access_token": access_token,
            }
        )


class OAuthHandler:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_access_token(self, code: str, name: str) -> dict:
        """
        Get access token.
        :param code: The pairing code
        :param name: The name of the device being paired
        :return:
        """
        query = OAuthHandlerHelper.get_access_token_query(code, name)
        response = requests.post(
            f"{BASE_URL}/ui/token?{query}", auth=(self.username, self.password)
        )
        response.raise_for_status()
        return json.loads(response.text)

    def get_new_access_token(self, refresh_token: str) -> dict:
        """
        Get new access token
        :param refresh_token: The refresh token
        :return: dict containing access token, and new refresh token
        """
        query = OAuthHandlerHelper.get_new_access_token_query(refresh_token)
        response = requests.post(
            f"{BASE_URL}/ui/token?{query}", auth=(self.username, self.password)
        )
        response.raise_for_status()
        return json.loads(response.text)

    def get_sid(self, access_token: str) -> str:
        """
        Get session ID.
        :param access_token: Valid access token
        :return: SID
        """
        query = OAuthHandlerHelper.get_sid_query(access_token)
        response = requests.get(
            f"{BASE_URL}/ui/sid?{query}", auth=(self.username, self.password)
        )
        response.raise_for_status()
        return json.loads(response.text).get("SID")


class AsyncOAuthHandler:
    def __init__(
        self, username: str, password: str, web_session: aiohttp.ClientSession
    ):
        self.username = username
        self.password = password
        self.web_session = web_session

    async def get_access_token(self, code: str, name: str) -> dict:
        """
        Get access token.
        :param code: The pairing code
        :param name: The name of the device being paired
        :return:
        """
        query = OAuthHandlerHelper.get_access_token_query(code, name)
        response = await self.web_session.post(
            f"{BASE_URL}/ui/token?{query}",
            auth=aiohttp.BasicAuth(self.username, self.password),
        )
        response.raise_for_status()
        return await response.json()

    async def get_new_access_token(self, refresh_token: str) -> dict:
        """
        Get new access token
        :param refresh_token: The refresh token
        :return: dict containing access token, and new refresh token
        """
        query = OAuthHandlerHelper.get_new_access_token_query(refresh_token)
        response = await self.web_session.post(
            f"{BASE_URL}/ui/token?{query}",
            auth=aiohttp.BasicAuth(self.username, self.password),
        )
        response.raise_for_status()
        return await response.json()

    async def get_sid(self, access_token: str) -> str:
        """
        Get session ID.
        :param access_token: Valid access token
        :return: SID
        """
        query = OAuthHandlerHelper.get_sid_query(access_token)
        response = await self.web_session.get(
            f"{BASE_URL}/ui/sid?{query}",
            auth=aiohttp.BasicAuth(self.username, self.password),
        )
        response.raise_for_status()
        response_json = await response.json()
        return response_json.get("SID")


class OAuthStorage:
    def __init__(self, path: str):
        self.path = path

    def store_access_token(self, payload: dict):
        expires_at = time.time() + payload["expires_in"]
        payload.update({"expires_at": expires_at})
        self.__store("access_token", payload)

    def fetch_access_token(self) -> Optional[dict]:
        return self.__fetch("access_token")

    def __store(self, payload_type: str, payload: dict):
        path = self.__get_path(payload_type)

        with open(path, "w") as f:
            content = json.dumps(payload)
            f.write(content)

    def __fetch(self, payload_type: str) -> Optional[dict]:
        path = self.__get_path(payload_type)

        if not os.path.exists(path):
            return None

        with open(path) as f:
            content = f.read()
            return json.loads(content)

    def __get_path(self, payload_type: str):
        return os.path.join(self.path, f"{payload_type}.json")


class OAuthWrapper:
    def __init__(self, oauth_handler: OAuthHandler, oauth_storage: OAuthStorage):
        self.oauth_handler = oauth_handler
        self.oauth_storage = oauth_storage

    def get_sid(self, code: str, name: str) -> str:
        """
        Get SID by providing the initial pairing code and the device name you would like to register.

        :param code: The code provided in the QR code
        :param name: The name of the device you want to register
        :return:
        """
        access_token = self.oauth_storage.fetch_access_token()

        if access_token is None:
            logger.debug("No token, requesting")
            access_token = self.oauth_handler.get_access_token(code, name)
            self.oauth_storage.store_access_token(access_token)

        expires_at = access_token["expires_at"]

        if expires_at < time.time():
            logger.debug("Token expired, refreshing")
            refreshed_token = self.oauth_handler.get_new_access_token(
                access_token["refresh_token"]
            )
            self.oauth_storage.store_access_token(refreshed_token)
            token = refreshed_token["access_token"]
        else:
            token = access_token["access_token"]

        return self.oauth_handler.get_sid(token)
