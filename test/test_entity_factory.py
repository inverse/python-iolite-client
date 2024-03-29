import unittest
from typing import Dict

from iolite_client import entity_factory
from iolite_client.entity import RadiatorValve
from iolite_client.exceptions import UnsupportedDeviceError

EXAMPLE_HEATER: Dict = {
    "properties": [
        {
            "timestamp": 1580472165268,
            "name": "valvePosition",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": True,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 22945785,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": 0.0,
            "predictions": [],
            "valueFriendlyName": "Closed",
            "ranges": [],
            "hashCode": 23808661,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580425966790,
            "name": "heatingMode",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": True,
            "requestedValue": None,
            "requestedValueTimestamp": 1580397443162,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 19818913,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": "Normal",
            "predictions": [],
            "hashCode": 23639409,
            "class": "TextProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580414086827,
            "name": "waterFeedTemperature",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 13792398,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": 45.0,
            "predictions": [],
            "valueFriendlyName": None,
            "ranges": [],
            "hashCode": 29146318,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580397428874,
            "name": "supportedCommunicationIntervals",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 27010580,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": "0,120,300,600,1200,1800,3600,28800",
            "predictions": [],
            "hashCode": 3342299,
            "class": "TextProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580472165268,
            "name": "currentEnvironmentTemperature",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 20061228,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": 19.0,
            "predictions": [],
            "valueFriendlyName": None,
            "ranges": [],
            "hashCode": 30576386,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580472165268,
            "name": "batteryLevel",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "BatteryLowDatapoint",
                "internal": False,
                "hashCode": 7283277,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": 100.0,
            "predictions": [],
            "valueFriendlyName": None,
            "ranges": [],
            "hashCode": 5645101,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580472165268,
            "name": "rssi",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 772429,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": -64.0,
            "predictions": [],
            "valueFriendlyName": "Very good",
            "ranges": [],
            "hashCode": 8125618,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580472165268,
            "name": "heatingTemperatureSetting",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": True,
            "requestedValue": None,
            "requestedValueTimestamp": 1580425366889,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 12950729,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": 6.5,
            "predictions": [],
            "valueFriendlyName": None,
            "ranges": [],
            "hashCode": 11690872,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580472165335,
            "name": "communicationInterval",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": True,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 29020087,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": 600,
            "predictions": [],
            "valueFriendlyName": None,
            "ranges": [],
            "hashCode": 5163525,
            "class": "IntegerProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1579794418064,
            "name": "repeaterRssi",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "FunctionValueAsStringDatapoint",
                "internal": False,
                "hashCode": 1073663,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": None,
            "predictions": [],
            "valueFriendlyName": "Very good",
            "ranges": [],
            "hashCode": 27860123,
            "class": "DoubleProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580472165268,
            "name": "windowStatusAssessment",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "OpenClosedToBooleanDatapoint",
                "internal": False,
                "hashCode": 9612915,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": False,
            "predictions": [],
            "hashCode": 18993657,
            "class": "BooleanProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 1580397429005,
            "name": "deviceStatus",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "readable": True,
            "writable": False,
            "requestedValue": None,
            "requestedValueTimestamp": 0,
            "dataPointConfiguration": {
                "configuration": {},
                "dataPointType": "IOLITEDeviceStatus",
                "internal": True,
                "hashCode": 2472974,
                "class": "DataPointConfiguration",
                "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
            },
            "value": "OK",
            "predictions": [],
            "hashCode": 441420,
            "class": "TextProperty",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
    ],
    "attributes": [
        {
            "timestamp": 0,
            "name": "gatewayIdentifier",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "value": "01932471",
            "hashCode": 28287297,
            "class": "TextAttribute",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
        {
            "timestamp": 0,
            "name": "configuredLocationName",
            "namespaceURI": "http://iolite.de",
            "element": "25561123",
            "value": "Bad",
            "hashCode": 32771072,
            "class": "TextAttribute",
            "ePackageURI": "http://www.iolite.de/models/Properties-2.0.ecore",
        },
    ],
    "graphicalSymbolURI": None,
    "started": True,
    "driverIdentifier": "enocean-ip-driver.jar",
    "typeNamespaceURI": "http://iolite.de",
    "typeName": "Heater",
    "dataPointConfiguration": {},
    "id": "id-1",
    "friendlyName": "Stellantrieb_0",
    "positionTimeStamp": 0,
    "placeIdentifier": "placeIdentifier-1",
    "environment": "7626396",
    "manufacturer": "Jaeger Direkt",
    "modelName": None,
    "hashCode": 25561123,
    "class": "Device",
    "ePackageURI": "http://www.iolite.de/environment-1.0.ecore",
}


class EntityTest(unittest.TestCase):
    def test_create_heater(self):
        heater = entity_factory.create_device(EXAMPLE_HEATER)
        self.assertIsInstance(heater, RadiatorValve)
        self.assertEqual("id-1", heater.identifier)
        self.assertEqual("Stellantrieb_0", heater.name)
        self.assertEqual(100, heater.battery_level)
        self.assertEqual(0, heater.valve_position)
        self.assertEqual(19, heater.current_env_temp)

    def test_create_device_unsupported_device(self):
        with self.assertRaises(UnsupportedDeviceError):
            entity_factory.create_device(
                {
                    "class": "Device",
                    "id": "yolo",
                    "placeIdentifier": "kitchen",
                    "typeName": "DeathStar",
                }
            )

    def test_create_device_unsupported_device_class(self):
        with self.assertRaises(NotImplementedError):
            entity_factory.create_device(
                {
                    "class": "DeathStar",
                    "id": "yolo",
                }
            )

    def test_create_device_missing_class(self):
        with self.assertRaises(ValueError):
            entity_factory.create_device(
                {
                    "id": "yolo",
                }
            )

    def test_create_device_missing_id(self):
        with self.assertRaises(ValueError):
            entity_factory.create_device(
                {
                    "class": "DeathStar",
                }
            )

    def test_create_room_unsupported_device_class(self):
        with self.assertRaises(NotImplementedError):
            entity_factory.create_device(
                {
                    "class": "DeathStar",
                    "id": "yolo",
                }
            )

    def test_create_room_missing_class(self):
        with self.assertRaises(ValueError):
            entity_factory.create_device(
                {
                    "id": "yolo",
                }
            )

    def test_create_room_missing_id(self):
        with self.assertRaises(ValueError):
            entity_factory.create_device(
                {
                    "class": "DeathStar",
                }
            )


if __name__ == "__main__":
    unittest.main()
