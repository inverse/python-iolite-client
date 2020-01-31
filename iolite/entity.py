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
    pass


def entity_factory(payload: dict) -> Optional[Entity]:
    entity_class = payload.get('class')
    type_name = payload.get('typeName')

    if entity_class == 'Room':
        return Room(payload.get('id'), payload.get('friendlyName'))

    if entity_class == 'Device' and type_name == 'Lamp':
        return Lamp(
            payload.get('id'),
            payload.get('friendlyName'),
            payload.get('manufacturer')
        )

    if entity_class == 'Device' and type_name == 'TwoChannelRockerSwitch':
        return Switch(
            payload.get('id'),
            payload.get('friendlyName'),
            payload.get('manufacturer')
        )

    if entity_class == 'Device' and type_name == 'Lamp':
        return Lamp(
            payload.get('id'),
            payload.get('friendlyName'),
            payload.get('manufacturer')
        )

    if entity_class == 'Device' and type_name == 'Heater':
        properties = payload.get('properties')

        current_env_temp = __get_prop(properties, 'currentEnvironmentTemperature')
        battery_level = __get_prop(properties, 'batteryLevel')
        heating_mode = __get_prop(properties, 'heatingMode')
        valve_position = __get_prop(properties, 'valvePosition')

        return RadiatorValve(
            payload.get('id'),
            payload.get('friendlyName'),
            payload.get('manufacturer'),
            current_env_temp,
            battery_level,
            heating_mode,
            valve_position
        )


def __get_prop(properties: list, key: str):
    result = list(filter(lambda prop: prop['name'] == key, properties))
    value = None
    if len(result) != 0:
        value = result[0]
    return value.get('value')
