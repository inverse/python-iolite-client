#!/usr/bin/env python

import asyncio
import os
from typing import NoReturn

import websockets
import json
import logging

from environs import Env
from base64 import b64encode

from iolite.request_handler import ClassMap, RequestHandler

logging.basicConfig(level=logging.INFO)

env = Env()
env.read_env()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
SID = os.getenv('SID')

user_pass = f'{USERNAME}:{PASSWORD}'

user_pass = b64encode(user_pass.encode()).decode('ascii')
headers = {'Authorization': f'Basic {user_pass}'}

request_handler = RequestHandler()


async def response_handler(response: str, websocket) -> NoReturn:
    response_dict = json.loads(response)
    response_class = response_dict.get('class')

    if response_class == ClassMap.SubscribeSuccess.value:
        logging.info('Handling SubscribeSuccess')
        for device in response_dict.get('initialValues'):
            logging.info(f'Setting up {device["placeName"]}')
    if response_class == ClassMap.QuerySuccess.value:
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


async def handler() -> NoReturn:
    uri = f'wss://remote.iolite.de/bus/websocket/application/json?SID={SID}'
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        request = request_handler.get_subscribe_request()
        await send_request(request, websocket)

        request = request_handler.get_query_request()
        await send_request(request, websocket)

        async for response in websocket:
            logging.info(f'Response received {response}', extra={'response': response})
            await response_handler(response, websocket)


asyncio.get_event_loop().run_until_complete(handler())
