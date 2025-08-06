# ble_advertising.py
from micropython import const
import struct

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x03)
_ADV_TYPE_UUID32_COMPLETE = const(0x05)
_ADV_TYPE_UUID128_COMPLETE = const(0x07)

def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None):
    payload = bytearray()

    flags = 0x02 if limited_disc else 0x06
    if br_edr:
        flags |= 0x18
    payload += struct.pack("BB", 2, _ADV_TYPE_FLAGS) + bytes([flags])

    if name:
        payload += struct.pack("BB", len(name) + 1, _ADV_TYPE_NAME) + name.encode()

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                payload += struct.pack("BB", len(b) + 1, _ADV_TYPE_UUID16_COMPLETE) + b
            elif len(b) == 4:
                payload += struct.pack("BB", len(b) + 1, _ADV_TYPE_UUID32_COMPLETE) + b
            elif len(b) == 16:
                payload += struct.pack("BB", len(b) + 1, _ADV_TYPE_UUID128_COMPLETE) + b

    return payload
