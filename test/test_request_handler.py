import unittest

from iolite.request_handler import RequestHandler, RequestOptions


class RequestHandlerTest(unittest.TestCase):
    def test_get_query_request(self):
        request_handler = RequestHandler()
        request = request_handler.get_query_request(
            "situationProfileModel", RequestOptions(should_stop=True)
        )
        self.assertIsNotNone(request["requestID"])

    def test_get_request(self):
        request_handler = RequestHandler()
        request = request_handler.get_query_request(
            "situationProfileModel", RequestOptions(should_stop=True)
        )
        retrieved_request = request_handler.get_request(request["requestID"])
        self.assertIsNotNone(retrieved_request)
        self.assertTrue(retrieved_request.request_options.should_stop)
