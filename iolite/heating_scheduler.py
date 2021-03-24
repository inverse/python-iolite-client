from base64 import b64encode
from enum import Enum
from typing import Tuple

import requests
from iolite.exceptions import IOLiteError

IOLITE_BASE_TEMP = 14
IOLITE_MAX_TEMP = 30


class Day(Enum):
    """Day constants for heating intervals.

    The heating interval API does not have the concept of days. Instead, an interval starting at 0 is considered Monday
    morning. To set the same interval on Tuesday, a 24 hour offset has to be set (in minutes).
    """

    MONDAY = 60 * 24 * 0
    TUESDAY = 60 * 24 * 1
    WEDNESDAY = 60 * 24 * 2
    THURSDAY = 60 * 24 * 3
    FRIDAY = 60 * 24 * 4
    SATURDAY = 60 * 24 * 5
    SUNDAY = 60 * 24 * 6


class HeatingSchedulerError(IOLiteError):
    pass


class HeatingScheduler(object):
    BASE_URL = "https://remote.iolite.de"
    HEATING_ENDPOINT = "/heating/api/heating/"

    def __init__(self, sid: str, username: str, password: str, room_id: str):
        """The HeatingScheduler comprises methods to interact with the heating interval API.

        :param sid: The session ID, used for authentication
        :param username: The username, used for authentication
        :param password: The password mathing the username, used for authentication
        :param room_id: The room to set or change the heating intervals for.
        """
        self.sid = sid
        self.username = username
        self.password = password
        self.room_id = room_id
        user_pass = f"{self.username}:{self.password}"
        self.auth_value = b64encode(user_pass.encode()).decode("ascii")

    def _prepare_request_arguments(self) -> Tuple[str, dict]:
        url = f"{self.BASE_URL}{self.HEATING_ENDPOINT}{self.room_id}"
        headers = {"Authorization": f"Basic {self.auth_value}"}
        params = {"SID": self.sid}
        return (
            url,
            {
                "headers": headers,
                "params": params,
            },
        )

    def set_comfort_temperature(self, temperature: float) -> requests.Response:
        """Sets the desired comfort temperature for all heating intervals.

        :param temperature: The temperature in degrees celcius
        :return: The API response
        """
        temperature_within_range = IOLITE_BASE_TEMP <= temperature <= IOLITE_MAX_TEMP
        if not temperature_within_range:
            raise HeatingSchedulerError(
                f"The desired comfort temperature has to be between "
                f"{IOLITE_BASE_TEMP} and {IOLITE_MAX_TEMP} degrees celsius."
            )
        url, params = self._prepare_request_arguments()
        response = requests.put(url, json={"comfortTemperature": temperature}, **params)
        return response

    def add_interval(
        self, day: Day, hour: int, minute: int, duration: int
    ) -> requests.Response:
        """Schedules a heating interval

        :param day: The day to set the interval for
        :param hour: The hour to begin the interval at
        :param minute: The minute of the hour to begin the interval at
        :param duration: The duration of for the interval to last in minutes
        :return: The API response, including the new interval's iolite ID
        """
        url, params = self._prepare_request_arguments()
        response = requests.post(
            url + "/intervals",
            json={
                "startTimeInMinutes": day.value + hour * 60 + minute,
                "durationInMinutes": duration,
            },
            **params,
        )
        return response

    def delete_interval(self, interval_id: str) -> requests.Response:
        """Deletes the given interval

        :param interval_id: iolite ID of the interval
        :return: The API response
        """
        url, params = self._prepare_request_arguments()
        response = requests.delete(url + f"/intervals/{interval_id}", **params)
        return response
