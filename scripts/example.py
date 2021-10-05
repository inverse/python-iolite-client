import logging
import sys

from environs import Env

from iolite.client import Client
from iolite.oauth_handler import OAuthHandler, OAuthStorage, OAuthWrapper

env = Env()
env.read_env()

USERNAME = env("HTTP_USERNAME")
PASSWORD = env("HTTP_PASSWORD")
CODE = env("CODE")
NAME = env("NAME")
LOG_LEVEL = env.log_level("LOG_LEVEL", logging.INFO)

logging.basicConfig(level=logging.getLevelName(LOG_LEVEL))
logger = logging.getLogger(__name__)

# Get SID
oauth_storage = OAuthStorage(".")
oauth_handler = OAuthHandler(USERNAME, PASSWORD)
oauth_wrapper = OAuthWrapper(oauth_handler, oauth_storage)
sid = oauth_wrapper.get_sid(CODE, NAME)

print("------------------")
print(f"URL: https://remote.iolite.de/ui/?SID={sid}")
print(f"User: {USERNAME}")
print(f"Pass: {PASSWORD}")
print("------------------")

# Init client
client = Client(sid, USERNAME, PASSWORD)

logger.info("Connecting to client")

client.discover()

logger.info("Finished discovery")

for room in client.discovered.get_rooms():
    print(f"{room.name} has {len(room.devices)} devices")
    if room.heating:
        print(
            f"Current temp: {room.heating.current_temp}, target: {room.heating.target_temp}"
        )

    for device in room.devices.values():
        print(f"- {device.name}")

bathroom = client.discovered.find_room_by_name("Bathroom")

if not bathroom:
    print("No discovered room called 'Bathroom'")
    sys.exit(1)

client.set_temp(next(iter(bathroom.devices.items()))[0], 0)
