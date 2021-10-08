import unittest

from iolite_client.entity import Heating, RadiatorValve, Room, Switch


class RoomTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bedroom = Room("placeIdentifier-1", "Bedroom")
        self.bedroom_switch = Switch(
            "2", "Bedroom Switch", self.bedroom.identifier, "Generic"
        )
        self.bedroom_radiator_valve = RadiatorValve(
            "3",
            "Bedroom Radiator Valve",
            self.bedroom.identifier,
            "Manu",
            21.5,
            55,
            "Normal",
            0.0,
        )
        self.bedroom_heating = Heating(self.bedroom.identifier, "Bedroom", 20.0, 21.5)

    def test_empty_room(self):
        self.assertEqual(0, len(self.bedroom.devices))

    def test_add_device(self):
        self.bedroom.add_device(self.bedroom_switch)
        self.assertEqual(1, len(self.bedroom.devices))
        self.assertEqual(
            self.bedroom_switch, self.bedroom.devices[self.bedroom_switch.identifier]
        )

    def test_add_device_again(self):
        self.bedroom.add_device(self.bedroom_radiator_valve)
        bedroom_radiator_valve = self.bedroom.devices[
            self.bedroom_radiator_valve.identifier
        ]
        self.assertEqual(
            bedroom_radiator_valve.current_env_temp,
            21.5,
        )
        bedroom_radiator_valve.current_env_temp = 25
        self.bedroom.add_device(bedroom_radiator_valve)
        bedroom_radiator_valve = self.bedroom.devices[
            self.bedroom_radiator_valve.identifier
        ]
        self.assertEqual(
            bedroom_radiator_valve.current_env_temp,
            25,
        )

    def test_room_has_device(self):
        self.bedroom.add_device(self.bedroom_switch)
        self.assertTrue(self.bedroom.has_device(self.bedroom_switch))

    def test_add_heating(self):
        self.bedroom.add_heating(self.bedroom_heating)
        self.assertEqual(self.bedroom.heating, self.bedroom_heating)


if __name__ == "__main__":
    unittest.main()
