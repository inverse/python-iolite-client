class IOLiteError(Exception):
    pass


class UnsupportedDeviceError(IOLiteError):
    def __init__(self, type_name: str, identifier: str, payload: dict):
        self.type_name = type_name
        self.identifier = identifier
        self.payload = payload
        super().__init__(f"Unsupported device with type_name {type_name} encountered")
