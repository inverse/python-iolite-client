import asyncio
import os
import websockets
import json
import logging

from typing import NoReturn
from environs import Env
from base64 import b64encode

from iolite.oauth_handler import OAuthHandler
from iolite.request_handler import ClassMap, RequestHandler

logging.basicConfig(level=logging.INFO)

env = Env()
env.read_env()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

user_pass = f'{USERNAME}:{PASSWORD}'

user_pass = b64encode(user_pass.encode()).decode('ascii')
headers = {'Authorization': f'Basic {user_pass}'}

request_handler = RequestHandler()

oauth_handler = OAuthHandler(USERNAME, PASSWORD)

SID = oauth_handler.get_sid(ACCESS_TOKEN)

BASE_URL = 'wss://remote.iolite.de'

DISCOVERED = {}


async def response_handler(response: str, websocket) -> NoReturn:
    response_dict = json.loads(response)
    response_class = response_dict.get('class')

    request = request_handler.get_request(response_dict.get('requestID'))

    if request is None:
        raise Exception('No matching request found')

    if response_class == ClassMap.SubscribeSuccess.value:
        logging.info('Handling SubscribeSuccess')

        if response_dict.get('requestID').startswith('places'):
            for value in response_dict.get('initialValues'):
                room_name = value.get('placeName')
                room_id = value.get('id')
                logging.info(f'Setting up {room_name}')
                DISCOVERED[room_id] = {
                    'name': room_name,
                    'devices': {},
                }

        if response_dict.get('requestID').startswith('devices'):
            for value in response_dict.get('initialValues'):
                room_id = value.get('placeIdentifier')

                if room_id not in DISCOVERED:
                    continue

                DISCOVERED[room_id]['devices'].update({
                    'id': value.get('id'),
                    'name': value.get('friendlyName'),
                })

    elif response_class == ClassMap.QuerySuccess.value:
        logging.info('Handling QuerySuccess')
    elif response_class == ClassMap.KeepAliveRequest.value:
        logging.info('Handling KeepAliveRequest')
        request = request_handler.get_keepalive_request()
        await send_request(request, websocket)
    else:
        logging.error(f'Unsupported response {response_dict}', extra={'response_class': response_class})


async def send_request(request: dict, websocket) -> NoReturn:
    request = json.dumps(request)
    await websocket.send(request)
    logging.info(f'Request sent {request}', extra={'request': request})


# TODO: Map to basic API
# - setup
# - update

async def handler() -> NoReturn:
    uri = f'{BASE_URL}/bus/websocket/application/json?SID={SID}'
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        request = request_handler.get_subscribe_request('places')
        await send_request(request, websocket)

        await asyncio.sleep(1)

        request = request_handler.get_subscribe_request('devices')
        await send_request(request, websocket)

        request = request_handler.get_query_request('situationProfileModel')
        await send_request(request, websocket)

        async for response in websocket:
            logging.info(f'Response received {response}', extra={'response': response})
            await response_handler(response, websocket)


asyncio.get_event_loop().run_until_complete(handler())
