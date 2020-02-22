import asyncio

import websockets
import json
import logging

from typing import NoReturn
from base64 import b64encode

from iolite.entity import EntityFactory, Room, Device
from iolite.request_handler import ClassMap, RequestHandler

logger = logging.getLogger(__name__)


class IOLiteClient:
    BASE_URL = 'wss://remote.iolite.de'

    def __init__(self, sid: str, username: str, password: str):
        self.discovered = []
        self.request_handler = RequestHandler()
        self.entity_factory = EntityFactory()
        self.sid = sid
        self.username = username
        self.password = password

    @staticmethod
    async def __send_request(request: dict, websocket) -> NoReturn:
        request = json.dumps(request)
        await websocket.send(request)
        logger.info(f'Request sent {request}', extra={'request': request})

    def __find_room_by_identifier(self, identifier: str) -> Room:
        match = None
        for room in self.discovered:
            if room.identifier == identifier:
                match = room
                break

        return match

    def __get_default_headers(self) -> dict:
        user_pass = f'{self.username}:{self.password}'
        user_pass = b64encode(user_pass.encode()).decode('ascii')
        headers = {'Authorization': f'Basic {user_pass}'}

        return headers

    async def __heating_handler(self) -> NoReturn:
        uri = f'{self.BASE_URL}/heating/ws?SID={self.sid}'
        async with websockets.connect(uri, extra_headers=self.__get_default_headers()) as websocket:
            async for response in websocket:
                logger.info(f'Response received (heating) {response}', extra={'response': response})

    async def __devices_handler(self) -> NoReturn:
        logger.info('Connecting to devices WS')
        uri = f'{self.BASE_URL}/devices/ws?SID={self.sid}'
        async with websockets.connect(uri, extra_headers=self.__get_default_headers()) as websocket:
            async for response in websocket:
                logger.info(f'Response received (device) {response}', extra={'response': response})

    async def __handler(self) -> NoReturn:
        logger.info('Connecting to JSON WS')
        uri = f'{self.BASE_URL}/bus/websocket/application/json?SID={self.sid}'
        async with websockets.connect(uri, extra_headers=self.__get_default_headers()) as websocket:

            # Get Rooms
            request = self.request_handler.get_subscribe_request('places')
            await self.__send_request(request, websocket)

            await asyncio.sleep(1)

            # Get Devices
            request = self.request_handler.get_subscribe_request('devices')
            await self.__send_request(request, websocket)

            request = self.request_handler.get_query_request('situationProfileModel')
            await self.__send_request(request, websocket)

            async for response in websocket:
                logger.info(f'Response received (JSON) {response}', extra={'response': response})
                await self.__response_handler(response, websocket)

    async def __response_handler(self, response: str, websocket) -> NoReturn:
        response_dict = json.loads(response)
        response_class = response_dict.get('class')

        if response_class == ClassMap.SubscribeSuccess.value:
            logger.info('Handling SubscribeSuccess')

            if response_dict.get('requestID').startswith('places'):
                for value in response_dict.get('initialValues'):
                    room = self.entity_factory.create(value)
                    logger.info(f'Setting up {room.name}')
                    self.discovered.append(room)

            if response_dict.get('requestID').startswith('devices'):
                for value in response_dict.get('initialValues'):
                    room_id = value.get('placeIdentifier')

                    room = self.__find_room_by_identifier(room_id)
                    if not room:
                        continue

                    device = self.entity_factory.create(value)
                    if not isinstance(device, Device):
                        logger.warning(f'Entity factory created unsupported class ({type(device).__name__})')
                        continue

                    logger.info(f'Adding {type(device).__name__} ({device.name}) to {room.name}')

                    room.add_device(device)

        elif response_class == ClassMap.QuerySuccess.value:
            logger.info('Handling QuerySuccess')
        elif response_class == ClassMap.KeepAliveRequest.value:
            logger.info('Handling KeepAliveRequest')
            request = self.request_handler.get_keepalive_request()
            await self.__send_request(request, websocket)
        elif response_class == ClassMap.ModelEventResponse.value:
            logger.info('Handling ModelEventResponse')
            pass
            # TODO: Update entity states
        else:
            logger.error(f'Unsupported response {response_dict}', extra={'response_class': response_class})

    def connect(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__handler())
        loop.create_task(self.__devices_handler())
        loop.run_forever()
