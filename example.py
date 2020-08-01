import logging
import os

from environs import Env

from iolite.client import IOLiteClient
from iolite.oauth_handler import OAuthHandler, OAuthStorage, OAuthWrapper

env = Env()
env.read_env()

USERNAME = os.getenv('HTTP_USERNAME')
PASSWORD = os.getenv('HTTP_PASSWORD')
CODE = os.getenv('CODE')
NAME = os.getenv('NAME')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)

logging.basicConfig(level=logging.getLevelName(LOG_LEVEL))
logger = logging.getLogger(__name__)

# Get SID
oauth_storage = OAuthStorage('.')
oauth_handler = OAuthHandler(USERNAME, PASSWORD)
oauth_wrapper = OAuthWrapper(oauth_handler, oauth_storage)
sid = oauth_wrapper.get_sid(CODE, NAME)

print('------------------')
print(f'URL: https://remote.iolite.de/ui/?SID={sid}')
print(f'User: {USERNAME}')
print(f'Pass: {PASSWORD}')
print('------------------')

# Init client
client = IOLiteClient(sid, USERNAME, PASSWORD)

logger.info('Connecting to client')

client.connect()

logger.info('Finished discovery')
