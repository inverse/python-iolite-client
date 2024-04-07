from abc import ABC
from typing import Dict, List, Optional


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

    @classmethod
    def get_type(cls) -> str:
        return cls.__name__.lower()


class Switch(Device):
    pass


class Blind(Device):
    def __init__(
        self,
        identifier: str,
        name: str,
        place_identifier: str,
        manufacturer: str,
        blind_level: int,
    ):
        super().__init__(identifier, name, place_identifier, manufacturer)
        self.blind_level = blind_level


class HumiditySensor(Device):
    def __init__(
        self,
        identifier: str,
        name: str,
        place_identifier: str,
        manufacturer: str,
        current_env_temp: float,
        humidity_level: float,
    ):
        super().__init__(identifier, name, place_identifier, manufacturer)
        self.current_env_temp = current_env_temp
        self.humidity_level = humidity_level


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


class InFloorValve(Device):
    def __init__(
        self,
        identifier: str,
        name: str,
        place_identifier: str,
        manufacturer: str,
        current_env_temp: float,
        heating_temperature_setting: float,
        device_status: str,
    ):
        super().__init__(identifier, name, place_identifier, manufacturer)
        self.heating_temperature_setting = heating_temperature_setting
        self.device_status = device_status
        self.current_env_temp = current_env_temp


class Heating(Entity):
    def __init__(
        self,
        identifier: str,
        name: str,
        current_temp: float,
        target_temp: float,
        window_open: Optional[bool],
    ):
        super().__init__(identifier, name)
        self.current_temp = current_temp
        self.target_temp = target_temp
        self.window_open = window_open


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

    def get_devices_by_type(self, device_type: str) -> List[Device]:
        return [
            device
            for device in self.devices.values()
            if device.get_type() == device_type
        ]
