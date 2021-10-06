import unittest

from iolite_client.entity import Heating, Room, Switch


class RoomTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bedroom = Room("placeIdentifier-1", "Bedroom")
        self.bedroom_switch = Switch(
            "2", "Bedroom Switch", self.bedroom.identifier, "Generic"
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

    def test_room_has_device(self):
        self.bedroom.add_device(self.bedroom_switch)
        self.assertTrue(self.bedroom.has_device(self.bedroom_switch))

    def test_add_heating(self):
        self.bedroom.add_heating(self.bedroom_heating)
        self.assertEqual(self.bedroom.heating, self.bedroom_heating)


if __name__ == "__main__":
    unittest.main()
