import logging
import sys

from environs import Env

from iolite_client.client import Client
from iolite_client.entity import RadiatorValve
from iolite_client.oauth_handler import LocalOAuthStorage, OAuthHandler, OAuthWrapper

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
oauth_storage = LocalOAuthStorage(".")
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
        if isinstance(device, RadiatorValve):
            print(f"  - current: {device.current_env_temp}")
            print(f"  - mode: {device.heating_mode}")

bathroom = client.discovered.find_room_by_name("Bathroom")

if not bathroom:
    print("No discovered room called 'Bathroom'")
    sys.exit(1)

client.set_temp(next(iter(bathroom.devices.items()))[0], 0)
