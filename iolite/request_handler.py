import secrets
import string
import time
from enum import Enum


class ClassMap(Enum):
    SubscribeRequest = "SubscribeRequest"
    SubscribeSuccess = "SubscribeSuccess"
    QueryRequest = "QueryRequest"
    QuerySuccess = "QuerySuccess"
    KeepAliveRequest = "KeepAliveRequest"
    KeepAliveResponse = "KeepAliveResponse"
    ActionRequest = "ActionRequest"
    ActionSuccess = "ActionSuccess"
    ModelEventResponse = "ModelEventResponse"


class RequestHandler:
    def __init__(self):
        self.request_stack = {}

    def get_subscribe_request(self, object_query: str) -> dict:
        request = self._build_request(
            object_query,
            {
                "modelID": "http://iolite.de#Environment",
                "class": ClassMap.SubscribeRequest.value,
                "objectQuery": object_query,
                "callback": "",
                "minimumUpdateInterval": 100,
            },
        )

        return request

    def get_action_request(self, device_id: str, temp: float) -> dict:
        request = self._build_request(
            ClassMap.ActionRequest.value,
            {
                "modelID": "http://iolite.de#Environment",
                "class": ClassMap.ActionRequest.value,
                "objectQuery": f"devices[id='{device_id}']/properties[name='heatingTemperatureSetting']",
                "actionName": "requestValueUpdate",
                "parameters": [
                    {
                        "class": "ValueParameter",
                        "value": temp,
                    }
                ],
            },
        )

        return request

    def get_query_request(self, query: str) -> dict:
        request = self._build_request(
            ClassMap.QueryRequest.value,
            {
                "modelID": "http://iolite.de#Environment",
                "class": ClassMap.QueryRequest.value,
                "query": query,
            },
        )

        return request

    @staticmethod
    def get_keepalive_request() -> dict:
        response = {
            "class": ClassMap.KeepAliveResponse.value,
            "responseAt": int(round(time.time() * 1000)),
        }

        return response

    def get_request(self, request_id: str) -> dict:
        return self.request_stack.get(request_id)

    def pop_request(self, request_id: str) -> dict:
        return self.request_stack.pop(request_id)

    def has_requests(self) -> bool:
        return len(self.request_stack) != 0

    def _build_request(
        self,
        prefix: str,
        request: dict,
    ) -> dict:
        request_id = self._get_request_id(prefix)
        request.update({"requestID": request_id})
        self.request_stack[request_id] = request

        return request

    def _get_request_id(self, prefix: str) -> str:
        while True:
            request_id = "".join(
                secrets.choice(string.ascii_letters) for _ in range(10)
            )
            request_id = f"{prefix}_{request_id}"
            if request_id not in self.request_stack:
                return request_id
