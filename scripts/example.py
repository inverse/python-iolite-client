import logging
import sys

from environs import Env

from iolite_client.client import Client
from iolite_client.entity import Blind, HumiditySensor, InFloorValve, RadiatorValve
from iolite_client.oauth_handler import LocalOAuthStorage, OAuthHandler, OAuthWrapper

env = Env()
env.read_env()

USERNAME = env("HTTP_USERNAME")
PASSWORD = env("HTTP_PASSWORD")
CLIENT_ID = env("CLIENT_ID")
CODE = env("CODE")
NAME = env("NAME")
LOG_LEVEL = env.log_level("LOG_LEVEL", logging.INFO)

logging.basicConfig(level=logging.getLevelName(LOG_LEVEL))
logger = logging.getLogger(__name__)

# Get SID
oauth_storage = LocalOAuthStorage(".")
oauth_handler = OAuthHandler(USERNAME, PASSWORD, CLIENT_ID)
oauth_wrapper = OAuthWrapper(oauth_handler, oauth_storage)

access_token = oauth_storage.fetch_access_token()
if not access_token:
    access_token = oauth_handler.get_access_token(CODE, NAME)
    oauth_storage.store_access_token(access_token)

sid = oauth_wrapper.get_sid(access_token)

print("------------------")
print(f"URL: https://remote.iolite.de/ui/?SID={sid}")
print(f"User: {USERNAME}")
print(f"Password: {PASSWORD}")
print(f"Client Id: {CLIENT_ID}")
print("------------------")

# Init client
client = Client(sid, USERNAME, PASSWORD)

logger.info("Connecting to client")

client.discover()

logger.info("Finished discovery")

for room in client.discovered.get_rooms():

    print(f"\n{room.name} has {len(room.devices)} devices")
    if room.heating:
        print(
            f"Current temp: {room.heating.current_temp}, target: {room.heating.target_temp}"
        )

    for device in room.devices.values():
        print(f"- {device.name} {device.get_type()}")
        if isinstance(device, RadiatorValve):
            print(f"  - current: {device.current_env_temp}")
            print(f"  - mode: {device.heating_mode}")
        if isinstance(device, InFloorValve):
            print(f"  - current: {device.current_env_temp}")
            print(f"  - setting: {device.heating_temperature_setting}")
        if isinstance(device, Blind):
            print(f"  - blind level: {device.blind_level}")
        if isinstance(device, HumiditySensor):
            print(f"  - temp: {device.current_env_temp}")
            print(f"  - humidity: {device.humidity_level}")

bathroom = client.discovered.find_room_by_name("Bathroom")

if not bathroom:
    print("No discovered room called 'Bathroom'")
    sys.exit(1)

client.set_temp(next(iter(bathroom.devices.items()))[0], 0)
