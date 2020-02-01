import os

from environs import Env

from iolite.client import IOLiteClient
from iolite.oauth_handler import OAuthHandler, OAuthStorage, OAuthWrapper

env = Env()
env.read_env()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
CODE = os.getenv('CODE')
NAME = os.getenv('NAME')


oauth_storage = OAuthStorage('.')
oauth_handler = OAuthHandler(USERNAME, PASSWORD)
oauth_wrapper = OAuthWrapper(oauth_handler, oauth_storage)
sid = oauth_wrapper.get_sid(CODE, NAME)

client = IOLiteClient(sid, USERNAME, PASSWORD)
client.connect()
