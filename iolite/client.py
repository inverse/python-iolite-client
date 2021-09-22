import asyncio
import json
import logging
from base64 import b64encode
from collections import defaultdict
from typing import Dict, List, Optional

import websockets

from iolite import entity_factory
from iolite.entity import Device, Room
from iolite.request_handler import ClassMap, RequestHandler

logger = logging.getLogger(__name__)


class Discovered:
    """Contains the discovered devices."""

    discovered_rooms: Dict[str, Room]
    unmapped_devices: defaultdict

    def __init__(self):
        self.discovered_rooms = {}
        self.unmapped_devices = defaultdict(list)

    def add_room(self, room: Room):
        """
        Add a room.

        :param room: The room to add
        :return:
        """
        self.discovered_rooms[room.identifier] = room

        if room.identifier in self.unmapped_devices:
            for device in self.unmapped_devices[room.identifier]:
                room.add_device(device)
            self.unmapped_devices.pop(room.identifier)

    def add_device(self, device: Device):
        """
        Add a device. If the room exists will map it, otherwise will add to unmapped dict.

        :param device: The device to add
        :return:
        """
        room = self.find_room_by_identifier(device.place_identifier)

        if room:
            room.add_device(device)
        else:
            self.unmapped_devices[device.place_identifier].append(device)

    def find_room_by_identifier(self, identifier: str) -> Optional[Room]:
        """Finds a room by the given identifier.

        :param identifier: The identifier
        :return: The matched room or None
        """
        return self._find_room_by_attribute_value("identifier", identifier)

    def find_room_by_name(self, name: str) -> Optional[Room]:
        """Finds a room by the given name.

        :param name: The name
        :return: The matched room or None
        """
        return self._find_room_by_attribute_value("name", name)

    def _find_room_by_attribute_value(
        self, attribute: str, value: str
    ) -> Optional[Room]:
        match = None
        for room in self.discovered_rooms.values():
            if getattr(room, attribute) == value:
                match = room
                break

        return match

    def get_rooms(self) -> List[Room]:
        """Returns all discovered rooms.

        :return: The list of discovered Room instances
        """
        return list(self.discovered_rooms.values())


class IOLiteClient:
    """The main client."""

    BASE_URL = "wss://remote.iolite.de"

    def __init__(self, sid: str, username: str, password: str):
        self.discovered = Discovered()
        self.request_handler = RequestHandler()
        self.sid = sid
        self.username = username
        self.password = password

    @staticmethod
    async def __send_request(request: dict, websocket):
        encoded_request = json.dumps(request)
        await websocket.send(encoded_request)
        logger.debug("Request sent", extra={"request": encoded_request})

    def __get_default_headers(self) -> dict:
        user_pass = f"{self.username}:{self.password}"
        user_pass = b64encode(user_pass.encode()).decode("ascii")
        headers = {"Authorization": f"Basic {user_pass}"}

        return headers

    async def __heating_handler(self):
        uri = f"{self.BASE_URL}/heating/ws?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self.__get_default_headers()
        ) as websocket:
            async for response in websocket:
                logger.debug(
                    f"Response received (heating) {response}",
                    extra={"response": response},
                )

    async def __devices_handler(self):
        logger.info("Connecting to devices WS")
        uri = f"{self.BASE_URL}/devices/ws?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self.__get_default_headers()
        ) as websocket:
            async for response in websocket:
                logger.debug(
                    f"Response received (device) {response}",
                    extra={"response": response},
                )

    async def __handler(self):
        logger.info("Connecting to JSON WS")
        uri = f"{self.BASE_URL}/bus/websocket/application/json?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self.__get_default_headers()
        ) as websocket:
            # Get Rooms
            request = self.request_handler.get_subscribe_request("places")
            await self.__send_request(request, websocket)

            # Get Devices
            request = self.request_handler.get_subscribe_request("devices")
            await self.__send_request(request, websocket)

            # Get Profiles
            request = self.request_handler.get_query_request("situationProfileModel")
            await self.__send_request(request, websocket)

            async for response in websocket:
                logger.debug(
                    f"Response received (JSON) {response}", extra={"response": response}
                )
                await self.__response_handler(response, websocket)

    async def __response_handler(self, response: str, websocket):
        response_dict = json.loads(response)
        response_class = response_dict.get("class")

        if response_class == ClassMap.SubscribeSuccess.value:
            logger.info("Handling SubscribeSuccess")

            if response_dict.get("requestID").startswith("places"):
                self.__handle_place_response(response_dict)

            if response_dict.get("requestID").startswith("devices"):
                self.__handle_device_response(response_dict)

        elif response_class == ClassMap.QuerySuccess.value:
            logger.info("Handling QuerySuccess")
        elif response_class == ClassMap.KeepAliveRequest.value:
            logger.info("Handling KeepAliveRequest")
            request = self.request_handler.get_keepalive_request()
            await self.__send_request(request, websocket)
        elif response_class == ClassMap.ModelEventResponse.value:
            logger.info("Handling ModelEventResponse")
            # TODO: Update entity states
        else:
            logger.error(
                f"Unsupported response {response_dict}",
                extra={"response_class": response_class},
            )

    def __handle_place_response(self, response_dict: dict):
        for value in response_dict["initialValues"]:
            room = entity_factory.create(value)
            if not isinstance(room, Room):
                logger.warning(
                    f"Entity factory created unsupported class ({type(room).__name__})"
                )
                continue

            self.discovered.add_room(room)
            logger.info(f"Setting up {room.name} ({room.identifier})")

    def __handle_device_response(self, response_dict: dict):
        for value in response_dict["initialValues"]:
            device = entity_factory.create(value)
            if not isinstance(device, Device):
                logger.warning(
                    f"Entity factory created unsupported class ({type(device).__name__})"
                )
                continue

            self.discovered.add_device(device)
            room = self.discovered.find_room_by_identifier(device.place_identifier)
            room_name = room.name if room else "unknown"
            logger.info(
                f"Adding {type(device).__name__} ({device.name}) to {room_name}"
            )

    def connect(self):
        """Connects to the remote endpoint of the heating system."""
        loop = asyncio.get_event_loop()
        loop.create_task(self.__handler())
        loop.create_task(self.__devices_handler())
        loop.run_forever()

    def discover(self):
        """Discovers the entities registered with the heating system."""
        asyncio.create_task(self.__handler())
        asyncio.create_task(self.__devices_handler())
