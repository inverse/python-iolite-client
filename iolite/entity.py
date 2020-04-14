from abc import ABC
from typing import Optional


class Entity(ABC):
    def __init__(self, identifier: str, name: str = None):
        self.identifier = identifier
        self.name = name


class Device(Entity):
    def __init__(self, identifier: str, name: str, manufacturer: str):
        super().__init__(identifier, name)
        self.manufacturer = manufacturer


class Switch(Device):
    pass


class Lamp(Device):
    pass


class RadiatorValve(Device):

    def __init__(self, identifier: str, name: str, manufacturer: str, current_env_temp: float, battery_level: int,
                 heating_mode: str,
                 valve_position: str):
        super().__init__(identifier, name, manufacturer)
        self.valve_position = valve_position
        self.heating_mode = heating_mode
        self.battery_level = battery_level
        self.current_env_temp = current_env_temp


class Room(Entity):
    def __init__(self, identifier: str, name: str = None):
        super().__init__(identifier, name)
        self.devices = {}

    def add_device(self, device: Device):
        self.devices[device.identifier] = device

    def has_device(self, device: Device) -> bool:
        return device.identifier in self.devices
