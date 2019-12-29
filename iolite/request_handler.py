import string
from enum import Enum
from random import random


class ClassMap(Enum):
    SubscribeRequest = 'SubscribeRequest'
    SubscribeSuccess = 'SubscribeSuccess'
    QueryRequest = 'QueryRequest'
    QuerySuccess = 'QuerySuccess'
    KeepAliveRequest = 'KeepAliveRequest'
    KeepAliveResponse = 'KeepAliveResponse'
    ActionRequest = 'ActionRequest'
    ActionSuccess = 'ActionSuccess'


class RequestHandler:

    def __init__(self):
        self.request_stack = {}

    def get_subscribe_request(self) -> dict:
        request = self._build_request('places', {
            'modelID': 'http://iolite.de#Environment',
            'class': ClassMap.SubscribeRequest.valu,
            'objectQuery': 'places',
            'callback': '',
            'minimumUpdateInterval': 100,
        })

        return request

    def get_action_request(self, room: str, temp: int) -> dict:
        request = self._build_request(ClassMap.ActionRequest.value, {
            'modelID': 'http://iolite.de#Environment',
            'class': ClassMap.ActionRequest.value,
            'objectQuery': f"devices[id='{room}']/properties[name='heatingTemperatureSetting']",
            'actionName': 'requestValueUpdate',
            'parameters': [
                {
                    'class': 'ValueParameter',
                    'value': temp,
                }
            ]
        })

        return request

    def _build_request(self, prefix: str, request: dict) -> dict:
        request_id = self._get_request_id(prefix)

        request.update({'RequestID': request_id})

        self.request_stack[request_id] = request

        return request

    def _get_request_id(self, prefix: str) -> str:
        letters = string.ascii_letters
        request_id = ''.join(random.choice(letters) for i in range(10))
        request_id =  f'{prefix}_{request_id}'

        while True:
            if request_id not in self.request_stack:
                return self._get_request_id(prefix)
