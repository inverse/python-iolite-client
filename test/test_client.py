import unittest

from iolite_client.client import Discovered
from iolite_client.entity import Heating, Room, Switch


class DiscoveredTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bedroom = Room("placeIdentifier-1", "Bedroom")
        self.kitchen = Room("placeIdentifier-2", "Kitchen")
        self.bedroom_switch = Switch(
            "2", "Bedroom Switch", self.bedroom.identifier, "Generic"
        )
        self.bedroom_heating = Heating(
            self.bedroom.identifier, "Bedroom", 10, 20, False
        )
        self.discovered = Discovered()

    def test_switch_without_room_is_unmapped(self):
        self.discovered.add_device(self.bedroom_switch)
        self.assertTrue(len(self.discovered.unmapped_entities) == 1)

    def test_previously_unmapped_switch_gets_mapped_to_room(self):
        self.discovered.unmapped_entities[self.bedroom_switch.place_identifier] = [
            self.bedroom_switch
        ]
        self.discovered.add_room(self.bedroom)
        self.assertTrue(len(self.discovered.unmapped_entities) == 0)
        self.assertEqual(
            self.bedroom_switch, self.bedroom.devices[self.bedroom_switch.identifier]
        )

    def test_switch_gets_mapped_to_existing_room(self):
        self.discovered.add_room(self.bedroom)
        self.discovered.add_device(self.bedroom_switch)
        self.assertTrue(len(self.discovered.unmapped_entities) == 0)
        self.assertEqual(
            self.bedroom_switch, self.bedroom.devices[self.bedroom_switch.identifier]
        )

    def test_get_rooms_returns_all_rooms(self):
        self.discovered.add_device(self.bedroom_switch)
        self.discovered.add_room(self.bedroom)
        self.discovered.add_room(self.kitchen)
        self.assertCountEqual(
            self.discovered.get_rooms(),
            [
                self.bedroom,
                self.kitchen,
            ],
            "Get rooms should yield all discovered rooms",
        )

    def test_find_room_by_name_returns_room(self):
        self.discovered.add_room(self.bedroom)
        self.discovered.add_room(self.kitchen)
        self.assertEqual(self.kitchen, self.discovered.find_room_by_name("Kitchen"))

    def test_find_room_by_identifier_returns_room(self):
        self.discovered.add_room(self.bedroom)
        self.discovered.add_room(self.kitchen)
        self.assertEqual(
            self.kitchen, self.discovered.find_room_by_identifier("placeIdentifier-2")
        )

    def test_add_heating(self):
        self.discovered.add_room(self.bedroom)
        self.discovered.add_heating(self.bedroom_heating)
        self.assertEqual(self.bedroom_heating, self.discovered.get_rooms()[0].heating)

    def test_add_heating_unmapped(self):
        self.discovered.add_heating(self.bedroom_heating)
        self.assertTrue(len(self.discovered.unmapped_entities) == 1)
        self.discovered.add_room(self.bedroom)
        self.assertTrue(len(self.discovered.unmapped_entities) == 0)
        self.assertEqual(self.bedroom_heating, self.discovered.get_rooms()[0].heating)

    def test_find_device_by_identifier(self):
        self.discovered.add_room(self.bedroom)
        self.discovered.add_device(self.bedroom_switch)
        self.assertEqual(
            self.bedroom_switch,
            self.discovered.find_device_by_identifier(self.bedroom_switch.identifier),
        )

    def test_find_device_by_identifier_unmapped(self):
        self.discovered.add_device(self.bedroom_switch)
        self.assertEqual(
            self.bedroom_switch,
            self.discovered.find_device_by_identifier(self.bedroom_switch.identifier),
        )

    def test_find_device_by_identifier_not_found(self):
        self.assertEqual(
            None,
            self.discovered.find_device_by_identifier(self.bedroom_switch.identifier),
        )


if __name__ == "__main__":
    unittest.main()
