import asyncio
import os
import websockets
import json
import logging

from typing import NoReturn
from environs import Env
from base64 import b64encode

from iolite.oauth_handler import OAuthHandler, OAuthStorage, OAuthWrapper
from iolite.request_handler import ClassMap, RequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

env = Env()
env.read_env()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
CODE = os.getenv('CODE')
NAME = os.getenv('NAME')

user_pass = f'{USERNAME}:{PASSWORD}'

user_pass = b64encode(user_pass.encode()).decode('ascii')
headers = {'Authorization': f'Basic {user_pass}'}

oauth_storage = OAuthStorage('.')
oauth_handler = OAuthHandler(USERNAME, PASSWORD)
oauth_wrapper = OAuthWrapper(oauth_handler, oauth_storage)
sid = oauth_wrapper.get_sid(CODE, NAME)


class IOLiteClient:
    BASE_URL = 'wss://remote.iolite.de'

    def __init__(self, sid: str):
        self.discovered = {}
        self.request_handler = RequestHandler()
        self.sid = sid

    async def send_request(self, request: dict, websocket) -> NoReturn:
        request = json.dumps(request)
        await websocket.send(request)
        logger.info(f'Request sent {request}', extra={'request': request})

    async def __handler(self) -> NoReturn:
        uri = f'{self.BASE_URL}/bus/websocket/application/json?SID={self.sid}'
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            request = self.request_handler.get_subscribe_request('places')
            await self.send_request(request, websocket)

            await asyncio.sleep(1)

            request = self.request_handler.get_subscribe_request('devices')
            await self.send_request(request, websocket)

            request = self.request_handler.get_query_request('situationProfileModel')
            await self.send_request(request, websocket)

            async for response in websocket:
                logger.info(f'Response received {response}', extra={'response': response})
                await self.response_handler(response, websocket)

    async def response_handler(self, response: str, websocket) -> NoReturn:
        response_dict = json.loads(response)
        response_class = response_dict.get('class')

        if response_class == ClassMap.SubscribeSuccess.value:
            logger.info('Handling SubscribeSuccess')

            if response_dict.get('requestID').startswith('places'):
                for value in response_dict.get('initialValues'):
                    room_name = value.get('placeName')
                    room_id = value.get('id')
                    logger.info(f'Setting up {room_name}')
                    self.discovered[room_id] = {
                        'name': room_name,
                        'devices': {},
                    }

            if response_dict.get('requestID').startswith('devices'):
                for value in response_dict.get('initialValues'):
                    room_id = value.get('placeIdentifier')

                    if room_id not in self.discovered:
                        continue

                    logger.info(f'Adding {value.get("friendlyName")} to {self.discovered[room_id]["name"]}')

                    self.discovered[room_id]['devices'].update({
                        'id': value.get('id'),
                        'name': value.get('friendlyName'),
                    })

        elif response_class == ClassMap.QuerySuccess.value:
            logger.info('Handling QuerySuccess')
        elif response_class == ClassMap.KeepAliveRequest.value:
            logger.info('Handling KeepAliveRequest')
            request = self.request_handler.get_keepalive_request()
            await self.send_request(request, websocket)
        else:
            logger.error(f'Unsupported response {response_dict}', extra={'response_class': response_class})

    def connect(self):
        asyncio.get_event_loop().run_until_complete(self.__handler())


client = IOLiteClient(sid)

client.connect()


