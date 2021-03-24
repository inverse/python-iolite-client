import unittest

from iolite.client import Discovered
from iolite.entity import Room, Switch


class DiscoveredTest(unittest.TestCase):
    def setUp(self) -> None:
        self.room_1 = Room("placeIdentifier-1", "Bedroom")
        self.room_2 = Room("placeIdentifier-2", "Kitchen")
        self.switch = Switch("2", "Bedroom Switch", "placeIdentifier-1", "Generic")
        self.discovered = Discovered()

    def test_switch_without_room_is_unmapped(self):
        self.discovered.add_device(self.switch)
        self.assertTrue(len(self.discovered.unmapped_devices) == 1)

    def test_previously_unmapped_switch_gets_mapped_to_room(self):
        self.discovered.unmapped_devices[self.switch.place_identifier] = [self.switch]
        self.discovered.add_room(self.room_1)
        self.assertTrue(len(self.discovered.unmapped_devices) == 0)
        self.assertEqual(self.switch, self.room_1.devices[self.switch.identifier])

    def test_switch_gets_mapped_to_existing_room(self):
        self.discovered.add_room(self.room_1)
        self.discovered.add_device(self.switch)
        self.assertTrue(len(self.discovered.unmapped_devices) == 0)
        self.assertEqual(self.switch, self.room_1.devices[self.switch.identifier])

    def test_get_rooms_returns_all_rooms(self):
        self.discovered.add_device(self.switch)
        self.discovered.add_room(self.room_1)
        self.discovered.add_room(self.room_2)
        self.assertCountEqual(
            self.discovered.get_rooms(),
            [
                self.room_1,
                self.room_2,
            ],
            "Get rooms should yield all discovered rooms",
        )

    def test_find_room_by_name_returns_room(self):
        self.discovered.add_room(self.room_1)
        self.discovered.add_room(self.room_2)
        self.assertEqual(self.room_2, self.discovered.find_room_by_name("Kitchen"))

    def test_find_room_by_identifier_returns_room(self):
        self.discovered.add_room(self.room_1)
        self.discovered.add_room(self.room_2)
        self.assertEqual(
            self.room_2, self.discovered.find_room_by_identifier("placeIdentifier-2")
        )


if __name__ == "__main__":
    unittest.main()
