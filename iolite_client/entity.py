from abc import ABC
from typing import Dict, Optional


class Entity(ABC):
    def __init__(self, identifier: str, name: str):
        self.identifier = identifier
        self.name = name


class PlaceEntity(Entity):
    def __init__(self, identifier: str, name: str, place_identifier: str):
        super().__init__(identifier, name)
        self.place_identifier = place_identifier


class Device(PlaceEntity):
    def __init__(
        self, identifier: str, name: str, place_identifier: str, manufacturer: str
    ):
        super().__init__(identifier, name, place_identifier)
        self.manufacturer = manufacturer


class Switch(Device):
    pass


class Lamp(Device):
    pass


class RadiatorValve(Device):
    def __init__(
        self,
        identifier: str,
        name: str,
        place_identifier: str,
        manufacturer: str,
        current_env_temp: float,
        battery_level: int,
        heating_mode: str,
        valve_position: float,
    ):
        super().__init__(identifier, name, place_identifier, manufacturer)
        self.valve_position = valve_position
        self.heating_mode = heating_mode
        self.battery_level = battery_level
        self.current_env_temp = current_env_temp


class Heating(Entity):
    def __init__(
        self, identifier: str, name: str, current_temp: float, target_temp: float
    ):
        super().__init__(identifier, name)
        self.current_temp = current_temp
        self.target_temp = target_temp


class Room(Entity):
    def __init__(self, identifier: str, name: str):
        super().__init__(identifier, name)
        self.devices: Dict[str, Device] = {}
        self.heating: Optional[Heating] = None

    def add_device(self, device: Device):
        if device.place_identifier != self.identifier:
            raise Exception(
                f"Trying to add device to wrong room {device.place_identifier} != {self.identifier}"
            )

        self.devices[device.identifier] = device

    def has_device(self, device: Device) -> bool:
        return device.identifier in self.devices

    def add_heating(self, heating: Heating):
        if heating.identifier != self.identifier:
            raise Exception(
                f"Trying to add heating to wrong room {heating.identifier} != {self.identifier}"
            )
        self.heating = heating
