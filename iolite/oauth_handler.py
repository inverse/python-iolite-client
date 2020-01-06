import json
from urllib.parse import urlencode
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class OAuthHandler:
    BASE_URL = 'https://remote.iolite.de'
    CLIENT_ID = 'deuwo_mia_app'

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_access_token(self, code: str, name: str):
        query = urlencode({
            'client_id': self.CLIENT_ID,
            'grant_type': 'authorization_code',
            'code': code,
            'name': name
        })

        try:
            response = requests.post(f'{self.BASE_URL}/ui/token?{query}', auth=(self.username, self.password))
            response.raise_for_status()
            return json.loads(response.text)
        except Exception as e:
            logger.exception(e)

    def get_refresh_token(self, refresh_token: str):
        query = urlencode({
            'client_id': self.CLIENT_ID,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        })

        try:
            response = requests.post(f'{self.BASE_URL}/ui/token?{query}', auth=(self.username, self.password))
            response.raise_for_status()
            return json.loads(response.text)
        except Exception as e:
            logger.exception(e)

    def get_sid(self, access_token: str):
        query = urlencode({
            'access_token': access_token,
        })

        try:
            response = requests.get(f'{self.BASE_URL}/ui/sid?{query}', auth=(self.username, self.password))
            response.raise_for_status()
            return json.loads(response.text).get('SID')
        except Exception as e:
            logger.exception(e)