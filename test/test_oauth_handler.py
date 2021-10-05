import datetime
import unittest
from unittest.mock import Mock

import responses
from freezegun import freeze_time
from iolite.oauth_handler import OAuthHandler, OAuthWrapper
from requests import HTTPError


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


class OAuthWrapperTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_oauth_handler = Mock()
        self.mock_oauth_storage = Mock()

    @freeze_time("2021-01-01 00:00:00")
    def test_get_sid_valid_access_token(self):
        self.mock_oauth_storage.fetch_access_token.return_value = {
            "expires_at": datetime.datetime(2021, 1, 1, 0, 0, 1).timestamp(),
            "access_token": "access-token",
        }

        oauth_wrapper = OAuthWrapper(self.mock_oauth_handler, self.mock_oauth_storage)

        oauth_wrapper.get_sid("my-code", "my-device")
        self.mock_oauth_handler.get_sid.assert_called_once_with("access-token")

    @freeze_time("2021-01-01 00:00:00")
    def test_get_sid_nothing_stored(self):
        self.mock_oauth_storage.fetch_access_token.return_value = None

        response = {
            "expires_at": datetime.datetime(2021, 1, 1, 0, 0, 1).timestamp(),
            "access_token": "access-token",
        }

        self.mock_oauth_handler.get_access_token.return_value = response

        oauth_wrapper = OAuthWrapper(self.mock_oauth_handler, self.mock_oauth_storage)

        oauth_wrapper.get_sid("my-code", "my-device")
        self.mock_oauth_storage.store_access_token.assert_called_once_with(response)
        self.mock_oauth_handler.get_sid.assert_called_once_with("access-token")

    @freeze_time("2021-01-01 00:00:01")
    def test_get_sid_expired_access_token(self):
        self.mock_oauth_storage.fetch_access_token.return_value = {
            "expires_at": datetime.datetime(2021, 1, 1, 0, 0, 0).timestamp(),
            "access_token": "access-token",
            "refresh_token": "refresh-token",
        }

        response = {
            "expires_at": datetime.datetime(2021, 1, 10, 0, 0, 0).timestamp(),
            "access_token": "access-token",
        }

        self.mock_oauth_handler.get_new_access_token.return_value = response

        oauth_wrapper = OAuthWrapper(self.mock_oauth_handler, self.mock_oauth_storage)
        oauth_wrapper.get_sid("my-code", "my-device")
        self.mock_oauth_handler.get_new_access_token.assert_called_once_with(
            "refresh-token"
        )
        self.mock_oauth_storage.store_access_token.assert_called_once_with(response)
        self.mock_oauth_handler.get_sid.assert_called_once_with("access-token")
