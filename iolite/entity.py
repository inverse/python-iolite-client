from abc import ABC
from typing import Optional


class Entity(ABC):
    def __init__(self, identifier: str, name: str):
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
    def __init__(self, identifier: str, name: str):
        super().__init__(identifier, name)
        self.devices = []

    def add_device(self, device: Device):
        self.devices.append(device)


class EntityFactory:

    def create(self, payload: dict) -> Optional[Entity]:
        """ Create entity from given payload. """
        entity_class = payload.get('class')
        type_name = payload.get('typeName')

        if entity_class == 'Room':
            return Room(payload.get('id'), payload.get('friendlyName'))
        elif entity_class == 'Device':
            return self.__create_device(type_name, payload)

    def __create_device(self, type_name: str, payload: dict):
        if type_name == 'Lamp':
            return Lamp(
                payload.get('id'),
                payload.get('friendlyName'),
                payload.get('manufacturer')
            )

        if type_name == 'TwoChannelRockerSwitch':
            return Switch(
                payload.get('id'),
                payload.get('friendlyName'),
                payload.get('manufacturer')
            )

        if type_name == 'Lamp':
            return Lamp(
                payload.get('id'),
                payload.get('friendlyName'),
                payload.get('manufacturer')
            )

        if type_name == 'Heater':
            properties = payload.get('properties')

            current_env_temp = self.__get_prop(properties, 'currentEnvironmentTemperature')
            battery_level = self.__get_prop(properties, 'batteryLevel')
            heating_mode = self.__get_prop(properties, 'heatingMode')
            valve_position = self.__get_prop(properties, 'valvePosition')

            return RadiatorValve(
                payload.get('id'),
                payload.get('friendlyName'),
                payload.get('manufacturer'),
                current_env_temp,
                battery_level,
                heating_mode,
                valve_position
            )

    @staticmethod
    def __get_prop(properties: list, key: str):
        """
        Get a property from list of properties.

        :param properties: The list of properties to filter on
        :param key: The property key
        :return:
        """
        result = list(filter(lambda prop: prop['name'] == key, properties))
        value = None
        if len(result) != 0:
            value = result[0]
        return value.get('value')
