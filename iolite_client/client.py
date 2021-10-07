import asyncio
import json
import logging
from base64 import b64encode
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import websockets

from iolite_client import entity_factory
from iolite_client.entity import Device, Heating, Room
from iolite_client.request_handler import ClassMap, RequestHandler

logger = logging.getLogger(__name__)


class Discovered:
    """Contains the discovered devices."""

    def __init__(self):
        self.discovered_rooms: Dict[str, Room] = {}
        self.unmapped_entities: defaultdict = defaultdict(list)

    def add_room(self, room: Room):
        """
        Add a room.

        :param room: The room to add
        :return:
        """
        self.discovered_rooms[room.identifier] = room

        if room.identifier in self.unmapped_entities:
            for entity in self.unmapped_entities[room.identifier]:
                if isinstance(entity, Heating):
                    room.add_heating(entity)
                else:
                    room.add_device(entity)
            self.unmapped_entities.pop(room.identifier)

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
            self.unmapped_entities[device.place_identifier].append(device)

    def add_heating(self, heating: Heating):
        """
        Add heating.

        :param heating: The heating to add
        :return:
        """
        room = self.find_room_by_identifier(heating.identifier)

        if room:
            room.add_heating(heating)
        else:
            self.unmapped_entities[heating.identifier].append(heating)

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

    def find_device_by_identifier(self, identifier: str) -> Optional[Device]:
        """Find a device by identifier.
        :param identifier: The identifier of the device
        :return: The matched device or None
        """
        for room in self.discovered_rooms.values():
            if room.devices.get(identifier):
                return room.devices.get(identifier)

        for devices in self.unmapped_entities.values():
            for device in devices:
                if device.identifier == identifier:
                    return device

        return None

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


@dataclass
class ClientResponse:
    abort: bool
    request: Optional[dict]

    @staticmethod
    def create_abort():
        return ClientResponse(True, None)

    @staticmethod
    def create_continue(request: Optional[dict] = None):
        return ClientResponse(False, request)


class Client:
    """The main client."""

    BASE_URL = "wss://remote.iolite.de"

    def __init__(self, sid: str, username: str, password: str):
        self.discovered = Discovered()
        self.request_handler = RequestHandler()
        self.sid = sid
        self.username = username
        self.password = password

    @staticmethod
    async def __send_request(request: Union[str, dict], websocket):
        if isinstance(request, dict):
            encoded_request = json.dumps(request)
        else:
            encoded_request = request
        await websocket.send(encoded_request)
        logger.debug("Request sent", extra={"request": encoded_request})

    def _get_default_headers(self) -> dict:
        user_pass = f"{self.username}:{self.password}"
        user_pass = b64encode(user_pass.encode()).decode("ascii")
        headers = {"Authorization": f"Basic {user_pass}"}

        return headers

    async def _fetch_heating(self):
        logger.info("Connecting to heating WS")
        uri = f"{self.BASE_URL}/heating/ws?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self._get_default_headers()
        ) as websocket:
            async for response in websocket:
                logger.debug(
                    f"Response received (heating) {response}",
                    extra={"response": response},
                )

                response = await self._heating_response_handler(response)
                if response.abort:
                    break

        logger.info("Finished heating WS")

    async def _devices_handler(self):
        logger.info("Connecting to devices WS")
        uri = f"{self.BASE_URL}/devices/ws?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self._get_default_headers()
        ) as websocket:
            async for response in websocket:
                logger.debug(
                    f"Response received (device) {response}",
                    extra={"response": response},
                )

            while True:
                await asyncio.sleep(5)
                await self.__send_request("keep_alive", websocket)

    async def _fetch_application(self, requests: list):
        logger.info("Connecting to JSON WS")
        uri = f"{self.BASE_URL}/bus/websocket/application/json?SID={self.sid}"
        async with websockets.connect(
            uri, extra_headers=self._get_default_headers()
        ) as websocket:
            for request in requests:
                await self.__send_request(request, websocket)

            async for response in websocket:
                logger.debug(
                    f"Response received (JSON) {response}", extra={"response": response}
                )
                response = await self._application_response_handler(response)
                if response.abort:
                    logger.info("Aborting")
                    break

                if response.request:
                    await self.__send_request(request, websocket)

            logger.info("Finished JSON WS")

    async def _heating_response_handler(self, response: str) -> ClientResponse:
        heatings_dict = json.loads(response)
        for heating_dict in heatings_dict:
            heating = entity_factory.create_heating(heating_dict)
            self.discovered.add_heating(heating)

        return ClientResponse.create_abort()

    async def _application_response_handler(self, response: str) -> ClientResponse:
        response_dict = json.loads(response)
        response_class = response_dict.get("class")

        if response_class == ClassMap.SubscribeSuccess.value:
            logger.info("Handling SubscribeSuccess")

            if response_dict.get("requestID").startswith("places"):
                self._handle_place_response(response_dict)

            if response_dict.get("requestID").startswith("devices"):
                self._handle_device_response(response_dict)

        elif response_class == ClassMap.QuerySuccess.value:
            logger.info("Handling QuerySuccess")
        elif response_class == ClassMap.KeepAliveRequest.value:
            logger.info("Handling KeepAliveRequest")
            request = self.request_handler.get_keepalive_request()
            return ClientResponse.create_continue(request)
        elif response_class == ClassMap.ModelEventResponse.value:
            logger.info("Handling ModelEventResponse")
        elif response_class == ClassMap.ActionSuccess.value:
            logger.info("Handling ActionSuccess")
        else:
            logger.warning(
                f"Unsupported response {response_dict}",
                extra={"response_class": response_class},
            )

        request_id = response_dict.get("requestID")
        if not request_id:
            return ClientResponse.create_continue()

        self.request_handler.pop_request(request_id)
        if not self.request_handler.has_requests():
            logger.info("Handled all requests")
            return ClientResponse.create_abort()

        return ClientResponse.create_continue()

    def _handle_place_response(self, response_dict: dict):
        for value in response_dict["initialValues"]:
            room = entity_factory.create(value)
            if not isinstance(room, Room):
                logger.warning(
                    f"Entity factory created unsupported class ({type(room).__name__})"
                )
                continue

            self.discovered.add_room(room)
            logger.info(f"Setting up {room.name} ({room.identifier})")

    def _handle_device_response(self, response_dict: dict):
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

    async def async_discover(self):
        requests = [
            # Get Rooms
            self.request_handler.get_subscribe_request("places"),
            # Get Devices
            self.request_handler.get_subscribe_request("devices"),
            # Get Profiles
            self.request_handler.get_query_request("situationProfileModel"),
        ]

        await asyncio.create_task(self._fetch_application(requests))
        await asyncio.create_task(self._fetch_heating())

    def discover(self):
        """Discovers the entities registered within the heating system."""
        asyncio.run(self.async_discover())

    async def async_set_temp(self, device, temp: float):
        request = self.request_handler.get_action_request(device, temp)
        await asyncio.create_task(self._fetch_application([request]))

    def set_temp(self, device, temp: float):
        asyncio.run(self.async_set_temp(device, temp))
