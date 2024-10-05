"""
MIT License

Copyright (c) 2024-present Simon Sawicki <contact@grub4k.xyz>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

https://github.com/Grub4K/qpb
"""

import ast
import base64
import contextlib
import enum
import io
import struct
from collections import defaultdict


def decode_protobuf(value):
    data = base64.b64decode(value)
    decoded = _decode(data)
    return decoded


def encode_protobuf(value):
    try:
        data = ast.literal_eval(value.strip())
        # data = ast.literal_eval(" ".join(value))
        result = _encode(data)
        encoded = base64.b64encode(result).decode()
        return encoded
    except SyntaxError:
        raise SyntaxError(f"invalid input: {value}")


class WireType(enum.IntEnum):
    VARINT = 0
    I64 = 1
    LEN = 2
    SGROUP = 3
    EGROUP = 4
    I32 = 5


_float_struct = struct.Struct(b"<f")
_double_struct = struct.Struct(b"<d")


def _encode(data) -> bytes:
    if not isinstance(data, dict):
        message = "type to encode has to be a dict"
        raise TypeError(message)

    return b"".join(_encode_record(value, wire_id) for wire_id, value in data.items())


def _decode(data):
    reader = data if isinstance(data, io.BufferedIOBase) else io.BytesIO(data)
    result = defaultdict(list)

    record = _read_record(reader)
    while record:
        key, value = record
        result[key].append(value)
        record = _read_record(reader)

    for key, values in result.items():
        for index, value in enumerate(values):
            if not isinstance(value, bytes):
                continue
            with contextlib.suppress(Exception):
                values[index] = _decode(value)
        if len(values) == 1:
            result[key] = values[0]

    return dict(result)


def _read_record(reader: io.BufferedIOBase):
    tag = _read_tag(reader)
    if tag is None:
        return None
    wire_id, wire_type = tag
    if wire_type == WireType.VARINT:
        value = _read_varint(reader)
    elif wire_type == WireType.I64:
        value = reader.read(8)
    elif wire_type == WireType.I32:
        value = reader.read(4)
    elif wire_type == WireType.LEN:
        value = reader.read(_read_varint(reader))
    else:
        message = "Unknown wire type"
        raise TypeError(message)

    return wire_id, value


def _encode_record(data, wire_id) -> bytes:
    if isinstance(data, int):
        if data < 0:
            data = _signed_to_zigzag(data)
        return _encode_tag(wire_id, WireType.VARINT) + _encode_varint(data)

    if isinstance(data, list):
        encoded = b"".join(map(_encode_record, data))
    elif isinstance(data, dict):
        encoded = _encode(data)
    elif isinstance(data, str):
        encoded = data.encode()
    elif isinstance(data, bytes):
        encoded = data
    else:
        message = f"Unencodable type: {type(data)}"
        raise TypeError(message)

    return _encode_tag(wire_id, WireType.LEN) + _encode_varint(len(encoded)) + encoded


def _read_varint(reader: io.BufferedIOBase):
    shift = 0
    data = 0

    byte = 0b1000_0000
    while byte & 0b1000_0000:
        result = reader.read(1)
        if not result:
            return None
        (byte,) = result
        data |= (byte & 0b0111_1111) << shift
        shift += 7

    return data


def _encode_varint(value: int) -> bytes:
    data_length = (value.bit_length() + 6) // 7 or 1
    data = bytearray(data_length)
    for index in range(data_length - 1):
        data[index] = value & 0b0111_1111 | 0b1000_0000
        value >>= 7

    data[-1] = value
    return bytes(data)


def _read_tag(reader: io.BufferedIOBase):
    value = _read_varint(reader)
    if value is None:
        return None
    return value >> 3, WireType(value & 0b111)


def _encode_tag(wire_id, wire_type: WireType) -> bytes:
    if wire_id is None:
        return b""
    return _encode_varint((wire_id << 3) | wire_type)


def _signed_to_zigzag(value: int):
    result = value << 1
    if value < 0:
        result = -result - 1
    return result
