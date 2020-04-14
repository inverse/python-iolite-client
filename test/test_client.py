import unittest

from iolite.client import Discovered
from iolite.entity import Room, Switch


class DiscoveredTest(unittest.TestCase):

    def test_unmapped(self):
        discovered = Discovered()
        switch = Switch('2', 'Bedroom Switch', 'placeIdentifier-1', 'Generic')
        discovered.add_device(switch)
        self.assertTrue(len(discovered.unmapped_devices) == 1)

        room = Room('placeIdentifier-1', 'Bedroom')
        discovered.add_room(room)
        self.assertTrue(len(discovered.unmapped_devices) == 0)
        self.assertEqual(switch, room.devices[switch.identifier])

    def test_already_mapped(self):
        discovered = Discovered()
        room = Room('placeIdentifier-1', 'Bedroom')

        discovered.add_room(room)
        switch = Switch('2', 'Bedroom Switch', 'placeIdentifier-1', 'Generic')
        discovered.add_device(switch)
        self.assertTrue(len(discovered.unmapped_devices) == 0)
        self.assertEqual(switch, room.devices[switch.identifier])


if __name__ == '__main__':
    unittest.main()
