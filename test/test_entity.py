import unittest

from iolite.entity import Room, Switch


class EntityTest(unittest.TestCase):

    def test_add_device_to_room(self):
        room = Room('1', 'Bedroom')
        switch = Switch('2', 'Bedroom Switch', 'Generic')
        room.add_device(switch)
        self.assertEqual(1, len(room.devices))
        self.assertEqual(switch, room.devices[switch.identifier])

    def test_room_has_device(self):
        room = Room('1', 'Bedroom')
        switch = Switch('2', 'Bedroom Switch', 'Generic')
        self.assertFalse(room.has_device(switch))
        room.add_device(switch)
        self.assertTrue(room.has_device(switch))


if __name__ == '__main__':
    unittest.main()
