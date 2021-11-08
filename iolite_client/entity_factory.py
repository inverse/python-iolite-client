from iolite_client.entity import Device, Heating, Lamp, RadiatorValve, Room, Switch
from iolite_client.exceptions import UnsupportedDeviceError


def create_room(payload: dict) -> Room:
    entity_class = payload.get("class")
    identifier = payload.get("id")

    if not entity_class:
        raise ValueError("Payload missing class")

    if not identifier:
        raise ValueError("Payload missing id")

    if entity_class != "Room":
        raise NotImplementedError(
            f"An unsupported entity class was provided when trying to create a room - {entity_class}"
        )

    return Room(identifier, payload["placeName"])


def create_device(payload: dict) -> Device:
    entity_class = payload.get("class")
    identifier = payload.get("id")

    if not entity_class:
        raise ValueError("Payload missing class")

    if not identifier:
        raise ValueError("Payload missing id")

    if entity_class != "Device":
        raise NotImplementedError(
            f"An unsupported entity class was provided when trying to create a device - {entity_class}"
        )

    return _create_device(identifier, payload["typeName"], payload)


def create_heating(payload: dict) -> Heating:
    return Heating(
        payload["id"],
        payload["name"],
        payload["currentTemperature"],
        payload["targetTemperature"],
    )


def _create_device(identifier: str, type_name: str, payload: dict):
    place_identifier = payload["placeIdentifier"]
    if type_name == "Lamp":
        return Lamp(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
        )
    elif type_name == "TwoChannelRockerSwitch":
        return Switch(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
        )
    elif type_name == "Lamp":
        return Lamp(
            identifier,
            payload["friendlyName"],
            place_identifier,
            payload["manufacturer"],
        )
    elif type_name == "Heater":
        properties = payload["properties"]

        current_env_temp = _get_prop(properties, "currentEnvironmentTemperature")
        battery_level = _get_prop(properties, "batteryLevel")
        heating_mode = _get_prop(properties, "heatingMode")
        valve_position = _get_prop(properties, "valvePosition")

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
    else:
        raise UnsupportedDeviceError(type_name, identifier, payload)


def _get_prop(properties: list, key: str):
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
