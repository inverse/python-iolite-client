import unittest
from base64 import b64encode

import responses
from iolite.heating_scheduler import (
    Day,
    HeatingScheduler,
    HeatingSchedulerError,
    Temperature,
)


class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sid = "MySID"
        username = "Charlie"
        password = "charlies_secret_password"  # nosec to disable hardcoded_password_string warning
        auth_value = b64encode(f"{username}:{password}".encode()).decode("ascii")
        cls.room_id = "placeIdentifier-1"
        cls.client = HeatingScheduler(sid, username, password, cls.room_id)

        cls.request_arguments = {
            "headers": {"Authorization": f"Basic {auth_value}"},
            "params": {"SID": "MySID"},
        }
        cls.scheduler_endpoint = (
            "https://remote.iolite.de/heating/api/heating/placeIdentifier-1"
        )

    def test_request_arguments_url(self):
        url, _ = self.client._prepare_request_arguments()
        self.assertEqual(
            self.scheduler_endpoint,
            url,
            "The URL should comprise the BASE_URL the HEATING_ENDPOINT and the room identifier:",
        )

    def test_sid_is_part_of_request_params(self):
        _, arguments = self.client._prepare_request_arguments()
        self.assertDictEqual(self.request_arguments, arguments)

    @responses.activate
    def test_comfort_temperature_gets_changed(self):
        responses.add(
            responses.PUT,
            self.scheduler_endpoint,
            match=[responses.json_params_matcher({"comfortTemperature": 20.5})],
        )
        self.client.set_comfort_temperature(20.5)
        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_comfort_temperature_is_at_least_14(self):
        with self.assertRaises(HeatingSchedulerError):
            self.client.set_comfort_temperature(13.9)

    @responses.activate
    def test_comfort_temperature_is_at_most_30(self):
        with self.assertRaises(HeatingSchedulerError):
            self.client.set_comfort_temperature(30.1)

    @responses.activate
    def test_interval_can_be_added_for_tuesday_2_30_pm(self):
        tuesday = 60 * 24
        two_thirty = 14 * 60 + 30
        responses.add(
            responses.POST,
            self.scheduler_endpoint + "/intervals",
            match=[
                responses.json_params_matcher(
                    {
                        "startTimeInMinutes": tuesday + two_thirty,
                        "durationInMinutes": 90,
                    }
                )
            ],
        )
        self.client.add_interval(Day.TUESDAY, 14, 30, 90)
        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_interval_deletion(self):
        responses.add(responses.DELETE, self.scheduler_endpoint + "/intervals/abc-def")
        self.client.delete_interval("abc-def")
        self.assertEqual(1, len(responses.calls))


class TestTemperature(unittest.TestCase):
    def test_within_range_valid(self):
        self.assertTrue(Temperature.within_range(14))
        self.assertTrue(Temperature.within_range(15))
        self.assertTrue(Temperature.within_range(30))

    def test_within_range_invalid(self):
        self.assertFalse(Temperature.within_range(13.9))
        self.assertFalse(Temperature.within_range(13))
        self.assertFalse(Temperature.within_range(-1))
        self.assertFalse(Temperature.within_range(30.1))
        self.assertFalse(Temperature.within_range(31))
        self.assertFalse(Temperature.within_range(9000))


if __name__ == "__main__":
    unittest.main()
