import unittest

import responses
from iolite.oauth_handler import OAuthHandler
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
