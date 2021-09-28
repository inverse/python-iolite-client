import unittest

from iolite.request_handler import RequestHandler


class RequestHandlerTest(unittest.TestCase):
    def test_get_query_request(self):
        request_handler = RequestHandler()
        request = request_handler.get_query_request("situationProfileModel")
        self.assertIsNotNone(request["requestID"])
