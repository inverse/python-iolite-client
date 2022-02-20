import asyncio
import datetime
import json
import unittest
from unittest.mock import Mock

import aiohttp
import pytest
import responses
from aioresponses import aioresponses
from freezegun import freeze_time
from requests import HTTPError

from iolite_client.oauth_handler import (
    AsyncOAuthHandler,
    OAuthHandler,
    OAuthHandlerHelper,
    OAuthWrapper,
)


class OAuthHandlerTest(unittest.TestCase):
    @responses.activate
    def test_get_access_token_invalid_credentials(self):
        responses.add(responses.POST, "https://remote.iolite.de/ui/token", status=403)
        oauth_handler = OAuthHandler("user", "password")
        with self.assertRaises(HTTPError):
            oauth_handler.get_access_token("dodgy-code", "my-device")

    @responses.activate
    def test_get_access_token_valid(self):
        responses.add(
            responses.POST,
            "https://remote.iolite.de/ui/token",
            json={
                "access_token": "token",
                "refresh_token": "refresh-token",
                "token_type": "BEARER",
                "expires_in": 604799,
                "expires_at": 1596878461.13904,
            },
        )
        oauth_handler = OAuthHandler("user", "password")
        response = oauth_handler.get_access_token("real-code", "my-device")
        self.assertIsInstance(response, dict)


class AsyncOAuthHandlerTest(unittest.TestCase):
    @staticmethod
    def _run_async(callback):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(callback())

    @pytest.mark.enable_socket
    def test_get_access_token_invalid_credentials(self):

        with aioresponses() as m:
            m.post("https://remote.iolite.de/ui/token", status=403)

            async def async_callback():
                async with aiohttp.ClientSession() as web_session:
                    oauth_handler = AsyncOAuthHandler("user", "password", web_session)
                    with self.assertRaises(
                        aiohttp.client_exceptions.ClientConnectionError
                    ):
                        await oauth_handler.get_access_token("dodgy-code", "my-device")

            self._run_async(async_callback)

    @pytest.mark.enable_socket
    def test_get_access_token_valid(self):
        with aioresponses() as m:
            query = OAuthHandlerHelper.get_access_token_query("real-code", "my-device")
            m.post(
                f"https://remote.iolite.de/ui/token?{query}",
                body=json.dumps(
                    {
                        "access_token": "token",
                        "refresh_token": "refresh-token",
                        "token_type": "BEARER",
                        "expires_in": 604799,
                        "expires_at": 1596878461.13904,
                    }
                ),
            )

            async def async_callback():
                async with aiohttp.ClientSession() as web_session:
                    oauth_handler = AsyncOAuthHandler("user", "password", web_session)
                    response = await oauth_handler.get_access_token(
                        "real-code", "my-device"
                    )
                    self.assertIsInstance(response, dict)

            self._run_async(async_callback)


class OAuthWrapperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_oauth_handler = Mock()
        self.mock_oauth_storage = Mock()
        self.oauth_wrapper = OAuthWrapper(
            self.mock_oauth_handler, self.mock_oauth_storage
        )

    @freeze_time("2021-01-01 00:00:00")
    def test_get_sid_valid_access_token(self):
        self.oauth_wrapper.get_sid(
            {
                "expires_at": datetime.datetime(2021, 1, 1, 0, 0, 1).timestamp(),
                "access_token": "access-token",
            }
        )
        self.mock_oauth_handler.get_sid.assert_called_once_with("access-token")

    @freeze_time("2021-01-01 00:00:01")
    def test_get_sid_expired_access_token(self):
        token = {
            "expires_at": datetime.datetime(2021, 1, 1, 0, 0, 0).timestamp(),
            "access_token": "access-token",
            "refresh_token": "refresh-token",
        }

        response = {
            "expires_at": datetime.datetime(2021, 1, 10, 0, 0, 0).timestamp(),
            "access_token": "access-token",
        }

        self.mock_oauth_handler.get_new_access_token.return_value = response

        self.oauth_wrapper.get_sid(token)
        self.mock_oauth_handler.get_new_access_token.assert_called_once_with(
            "refresh-token"
        )
        self.mock_oauth_storage.store_access_token.assert_called_once_with(response)
        self.mock_oauth_handler.get_sid.assert_called_once_with("access-token")

    @freeze_time("2021-01-01 00:00:00")
    def test_invalid_token_refresh(self):

        token = {
            "expires_at": datetime.datetime(2021, 1, 1, 0, 0, 1).timestamp(),
            "access_token": "access-token",
            "refresh_token": "refresh-token",
        }

        self.mock_oauth_storage.fetch_access_token.return_value = token

        self.mock_oauth_handler.get_sid.side_effect = [
            HTTPError("Something went wrong"),
            "sid",
        ]

        response = {
            "expires_at": datetime.datetime(2021, 1, 10, 0, 0, 0).timestamp(),
            "access_token": "access-token",
        }

        self.mock_oauth_handler.get_new_access_token.return_value = response

        oauth_wrapper = OAuthWrapper(self.mock_oauth_handler, self.mock_oauth_storage)
        oauth_wrapper.get_sid(token)

        self.assertEqual(self.mock_oauth_handler.get_sid.call_count, 2)
