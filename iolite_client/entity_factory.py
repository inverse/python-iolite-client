from typing import Optional

from iolite_client.entity import Entity, Heating, Lamp, RadiatorValve, Room, Switch


def create(payload: dict) -> Optional[Entity]:
    """Create entity from given payload."""
    entity_class = payload.get("class")
    identifier = payload.get("id")

    if not entity_class:
        raise Exception("Payload missing class")

    if not identifier:
        raise Exception("Payload missing id")

    if entity_class == "Room":
        return Room(identifier, payload["placeName"])
    elif entity_class == "Device":
        return __create_device(identifier, payload["typeName"], payload)
    else:
        raise NotImplementedError(
            f"An unsupported entity type was returned {entity_class}"
        )


def create_heating(payload: dict) -> Heating:
    return Heating(
        payload["id"],
        payload["name"],
        payload["currentTemperature"],
        payload["targetTemperature"],
    )


def __create_device(identifier: str, type_name: str, payload: dict):

    place_identifier = payload["placeIdentifier"]

    if type_name == "Lamp":
        return Lamp(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
        )

    if type_name == "TwoChannelRockerSwitch":
        return Switch(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
        )

    if type_name == "Lamp":
        return Lamp(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
        )

    if type_name == "Heater":
        properties = payload["properties"]

        current_env_temp = __get_prop(properties, "currentEnvironmentTemperature")
        battery_level = __get_prop(properties, "batteryLevel")
        heating_mode = __get_prop(properties, "heatingMode")
        valve_position = __get_prop(properties, "valvePosition")

        return RadiatorValve(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
            current_env_temp,
            battery_level,
            heating_mode,
            valve_position,
        )


def __get_prop(properties: list, key: str):
    """
    Get a property from list of properties.

    :param properties: The list of properties to filter on
    :param key: The property key
    :return:
    """
    result = list(filter(lambda prop: prop["name"] == key, properties))

    if len(result) == 0:
        raise ValueError(f"Failed to find {key} in property set")

    return result[0]["value"]
