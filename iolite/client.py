import asyncio
import json
import logging
from base64 import b64encode
from typing import NoReturn, Optional

import websockets
from iolite import entity_factory
from iolite.entity import Device, Room
from iolite.request_handler import ClassMap, RequestHandler

logger = logging.getLogger(__name__)


class Discovered:
    """ Contains the discovered devices. """

    discovered: dict
    unmapped_devices: dict

    def __init__(self):
        self.discovered = {}
        self.unmapped_devices = {}

    def add_room(self, room: Room) -> NoReturn:
        """
        Add a room.

        :param room: The room to add
        :return:
        """
        self.discovered[room.identifier] = room

        if room.identifier in self.unmapped_devices:
            for device in self.unmapped_devices[room.identifier]:
                room.add_device(device)
            self.unmapped_devices.pop(room.identifier)

    def add_device(self, device: Device) -> NoReturn:
        """
        Add a device. If the room exists will map it, otherwise will add to unmapped dict.

        :param device: The device to add
        :return:
        """
        room = self.find_room_by_identifier(device.place_identifier)

        if not room:
            if device.place_identifier not in self.unmapped_devices:
                self.unmapped_devices[device.place_identifier] = []

            self.unmapped_devices[device.place_identifier].append(device)

            return

        room.add_device(device)

    def find_room_by_identifier(self, identifier: str) -> Optional[Room]:
        """
        Find a room by the given identifier.

        :param identifier: The identifier
        :return: The matched room or None
        """
        match = None
        for room in self.discovered.values():
            if room.identifier == identifier:
                match = room
                break

        return match


class IOLiteClient:
    """ The main client. """

    BASE_URL = "wss://remote.iolite.de"

    def __init__(self, sid: str, username: str, password: str):
        self.discovered = Discovered()
        self.request_handler = RequestHandler()
        self.sid = sid
        self.username = username
        self.password = password

    @staticmethod
    async def __send_request(request: dict, websocket) -> NoReturn:
        request = json.dumps(request)
        await websocket.send(request)
        logger.debug(f"Request sent {request}", extra={"request": request})

    def __get_default_headers(self) -> dict:
        user_pass = f"{self.username}:{self.password}"
        user_pass = b64encode(user_pass.encode()).decode("ascii")
        headers = {"Authorization": f"Basic {user_pass}"}

        return headers

    async def __heating_handler(self) -> NoReturn:
        uri = f"{self.BASE_URL}/heating/ws?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self.__get_default_headers()
        ) as websocket:
            async for response in websocket:
                logger.debug(
                    f"Response received (heating) {response}",
                    extra={"response": response},
                )

    async def __devices_handler(self) -> NoReturn:
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

    async def __handler(self) -> NoReturn:
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

    async def __response_handler(self, response: str, websocket) -> NoReturn:
        response_dict = json.loads(response)
        response_class = response_dict.get("class")

        if response_class == ClassMap.SubscribeSuccess.value:
            logger.info("Handling SubscribeSuccess")

            if response_dict.get("requestID").startswith("places"):
                for value in response_dict.get("initialValues"):
                    room = entity_factory.create(value)
                    if not isinstance(room, Room):
                        logger.warning(
                            f"Entity factory created unsupported class ({type(room).__name__})"
                        )
                        continue

                    self.discovered.add_room(room)
                    logger.info(f"Setting up {room.name} ({room.identifier})")

            if response_dict.get("requestID").startswith("devices"):
                for value in response_dict.get("initialValues"):
                    device = entity_factory.create(value)
                    if not isinstance(device, Device):
                        logger.warning(
                            f"Entity factory created unsupported class ({type(device).__name__})"
                        )
                        continue

                    self.discovered.add_device(device)
                    room = self.discovered.find_room_by_identifier(
                        device.place_identifier
                    )
                    room_name = room.name or "unknown"
                    logger.info(
                        f"Adding {type(device).__name__} ({device.name}) to {room_name}"
                    )

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

    def connect(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__handler())
        loop.create_task(self.__devices_handler())
        loop.run_forever()
