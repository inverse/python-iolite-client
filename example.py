import logging
import os
import time

from environs import Env

from iolite.client import IOLiteClient
from iolite.oauth_handler import OAuthHandler, OAuthStorage, OAuthWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Env()
env.read_env()

USERNAME = os.getenv('HTTP_USERNAME')
PASSWORD = os.getenv('HTTP_PASSWORD')
CODE = os.getenv('CODE')
NAME = os.getenv('NAME')

# Get SID
oauth_storage = OAuthStorage('.')
oauth_handler = OAuthHandler(USERNAME, PASSWORD)
oauth_wrapper = OAuthWrapper(oauth_handler, oauth_storage)
sid = oauth_wrapper.get_sid(CODE, NAME)

# Init client
client = IOLiteClient(sid, USERNAME, PASSWORD)

logger.info('Connecting to client')

client.connect()

logger.info('Finished discovery')
