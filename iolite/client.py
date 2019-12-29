#!/usr/bin/env python

import asyncio
import os

import websockets
import json
import logging

from environs import Env
from enum import Enum
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


def response_handler(response: str):
    response_dict = json.loads(response)

    response_class = response_dict.get('class')

    if response_class == ClassMap.SubscribeSuccess.value:
        _handle_subscribe_success(response_dict)
    elif response_class == ClassMap.KeepAliveRequest.value:
        logging.info('Handling KeepAliveRequest')
    else:
        logging.error('Unsupported response class', extra={'response_class': response_class})


def _handle_subscribe_success(response: dict):
    pass


async def handler():
    uri = f'wss://remote.iolite.de/bus/websocket/application/json?SID={SID}'
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        request = request_handler.get_subscribe_request()
        request = json.dumps(request)
        await websocket.send(request)
        logging.info(f'Request sent {request}', extra={'request': request})

        response = await websocket.recv()
        logging.info(f'Response received {response}', extra={'response': response})
        response_handler(response)


asyncio.get_event_loop().run_until_complete(handler())
