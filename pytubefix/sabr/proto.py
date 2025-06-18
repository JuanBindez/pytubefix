import struct
from typing import Callable


def assert_uint32(value):
    if not (0 <= value <= 0xFFFFFFFF):
        raise ValueError("Value is not a valid uint32")

def assert_int32(value):
    if not (-0x80000000 <= value <= 0x7FFFFFFF):
        raise ValueError("Value is not a valid int32")

def varint32write(value, buf):
    while value > 0x7F:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    buf.append(value)

def varint64write(lo, hi, buf):
    for _ in range(9):  # max 10 bytes
        if hi == 0 and lo < 0x80:
            buf.append(lo)
            return
        buf.append((lo & 0x7F) | 0x80)
        carry = (lo >> 7)
        lo = ((hi << 25) | (lo >> 7)) & 0xFFFFFFFF
        hi = hi >> 7
    buf.append(lo)

def read_varint32(buf: bytes, pos: int):
    result = shift = 0
    while True:
        if pos >= len(buf):
            raise EOFError("Unexpected end of buffer while reading varint32")
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
        if shift > 35:
            raise ValueError("Varint32 too long")
    return result, pos

def read_varint64(buf, pos):
    low_bits = 0
    high_bits = 0


    for shift in range(0, 28, 7):
        b = buf[pos]
        pos += 1
        low_bits |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return low_bits, high_bits, pos

    middle_byte = buf[pos]
    pos += 1
    low_bits |= (middle_byte & 0x0F) << 28
    high_bits = (middle_byte & 0x70) >> 4
    if (middle_byte & 0x80) == 0:
        return low_bits, high_bits, pos

    for shift in range(3, 32, 7):
        b = buf[pos]
        pos += 1
        high_bits |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return low_bits, high_bits, pos

    raise ValueError("invalid varint")

def decode_int64(lo: int, hi: int) -> int:
    value = (hi << 32) | lo
    if hi & 0x80000000:
        value -= 1 << 64
    return value

def decode_uint64(lo: int, hi: int) -> int:
    return (hi << 32) | lo


class ProtoInt64:
    @staticmethod
    def enc(value: int):
        """Signed 64-bit -> lo/hi pair (int32 each)."""
        if value < 0:
            value += 1 << 64
        lo = value & 0xFFFFFFFF
        hi = (value >> 32) & 0xFFFFFFFF
        return {'lo': lo, 'hi': hi}

    @staticmethod
    def uEnc(value: int):
        """Unsigned 64-bit -> lo/hi pair (int32 each)."""
        lo = value & 0xFFFFFFFF
        hi = (value >> 32) & 0xFFFFFFFF
        return {'lo': lo, 'hi': hi}

class BinaryWriter:
    def __init__(self, encode_utf8: Callable[[str], bytes] = lambda s: s.encode('utf-8')):
        self.encode_utf8 = encode_utf8
        self.stack = []
        self.chunks = []
        self.buf = bytearray()

    def finish(self) -> bytes:
        if self.buf:
            self.chunks.append(bytes(self.buf))
            self.buf.clear()
        return b''.join(self.chunks)

    def fork(self):
        self.stack.append((self.chunks, self.buf))
        self.chunks = []
        self.buf = bytearray()
        return self

    def join(self):
        chunk = self.finish()
        if not self.stack:
            raise RuntimeError("Invalid state, fork stack empty")
        self.chunks, self.buf = self.stack.pop()
        self.uint32(len(chunk))
        return self.raw(chunk)

    def tag(self, field_no: int, wire_type: int):
        return self.uint32((field_no << 3) | wire_type)

    def raw(self, chunk: bytes):
        if self.buf:
            self.chunks.append(bytes(self.buf))
            self.buf.clear()
        self.chunks.append(chunk)
        return self

    def uint32(self, value: int):
        assert_uint32(value)
        varint32write(value, self.buf)
        return self

    def int32(self, value: int):
        assert_int32(value)
        varint32write(value & 0xFFFFFFFF, self.buf)
        return self

    def bool(self, value: bool):
        self.buf.append(1 if value else 0)
        return self

    def bytes(self, value: bytes):
        self.uint32(len(value))
        return self.raw(value)

    def string(self, value: str):
        encoded = self.encode_utf8(value)
        self.uint32(len(encoded))
        return self.raw(encoded)

    def float(self, value: float):
        self.raw(struct.pack('<f', value))
        return self

    def double(self, value: float):
        self.raw(struct.pack('<d', value))
        return self

    def fixed32(self, value: int):
        assert_uint32(value)
        self.raw(struct.pack('<I', value))
        return self

    def sfixed32(self, value: int):
        assert_int32(value)
        self.raw(struct.pack('<i', value))
        return self

    def sint32(self, value: int):
        assert_int32(value)
        encoded = (value << 1) ^ (value >> 31)
        varint32write(encoded, self.buf)
        return self

    def sfixed64(self, value: int):
        tc = ProtoInt64.enc(value)
        self.raw(struct.pack('<ii', tc['lo'], tc['hi']))
        return self

    def fixed64(self, value: int):
        tc = ProtoInt64.uEnc(value)
        self.raw(struct.pack('<II', tc['lo'], tc['hi']))
        return self

    def int64(self, value: int):
        tc = ProtoInt64.enc(value)
        varint64write(tc['lo'], tc['hi'], self.buf)
        return self

    def sint64(self, value: int):
        tc = ProtoInt64.enc(value)
        sign = tc['hi'] >> 31
        lo = (tc['lo'] << 1) ^ sign
        hi = ((tc['hi'] << 1) | (tc['lo'] >> 31)) ^ sign
        varint64write(lo, hi, self.buf)
        return self

    def uint64(self, value: int):
        tc = ProtoInt64.uEnc(value)
        varint64write(tc['lo'], tc['hi'], self.buf)
        return self


class BinaryReader:
    def __init__(self, buf, decode_utf8: Callable[[bytes], str] = lambda b: b.decode('utf-8')):
        if isinstance(buf, list):
            buf = bytes(buf)
        elif isinstance(buf, bytearray):
            buf = bytes(buf)
        elif not isinstance(buf, bytes):
            raise TypeError(f"Unsupported buffer type: {type(buf)}")

        self.decode_utf8 = decode_utf8
        self.buf = buf
        self.len = len(buf)
        self.pos = 0

    def tag(self):
        tag, self.pos = read_varint32(self.buf, self.pos)
        field_no = tag >> 3
        wire_type = tag & 0x7
        if field_no <= 0 or wire_type < 0 or wire_type > 5:
            raise ValueError(f"Illegal tag: field no {field_no} wire type {wire_type}")
        return field_no, wire_type

    def skip(self, wire_type: int, field_no=None):
        start = self.pos
        if wire_type == 0:  # Varint
            while self.buf[self.pos] & 0x80:
                self.pos += 1
            self.pos += 1
        elif wire_type == 1:  # 64-bit
            self.pos += 8
        elif wire_type == 2:  # Length-delimited
            length, self.pos = read_varint32(self.buf, self.pos)
            self.pos += length
        elif wire_type == 3:  # Start group
            while True:
                fn, wt = self.tag()
                if wt == 4:  # End group
                    if field_no is not None and fn != field_no:
                        raise ValueError("Invalid end group tag")
                    break
                self.skip(wt, fn)
        elif wire_type == 5:  # 32-bit
            self.pos += 4
        else:
            raise ValueError(f"Can't skip unknown wire type {wire_type}")
        self.assert_bounds()
        return self.buf[start:self.pos]

    def assert_bounds(self):
        if self.pos > self.len:
            raise EOFError("Premature EOF")

    def uint32(self):
        value, self.pos = read_varint32(self.buf, self.pos)
        return value

    def int32(self):
        return self.uint32() | 0

    def sint32(self):
        value = self.uint32()
        return (value >> 1) ^ -(value & 1)

    def varint64(self):
        lo, hi, self.pos = read_varint64(self.buf, self.pos)
        return lo, hi

    def int64(self):
        return decode_int64(*self.varint64())

    def uint64(self):
        return decode_uint64(*self.varint64())

    def sint64(self):
        lo, hi = self.varint64()
        sign = -(lo & 1)
        lo = ((lo >> 1) | ((hi & 1) << 31)) ^ sign
        hi = (hi >> 1) ^ sign
        return decode_int64(lo, hi)

    def bool(self):
        lo, hi = self.varint64()
        return lo != 0 or hi != 0

    def fixed32(self):
        value = struct.unpack_from('<I', self.buf, self.pos)[0]
        self.pos += 4
        return value

    def sfixed32(self):
        value = struct.unpack_from('<i', self.buf, self.pos)[0]
        self.pos += 4
        return value

    def fixed64(self):
        lo = self.sfixed32()
        hi = self.sfixed32()
        return decode_uint64(lo, hi)

    def sfixed64(self):
        lo = self.sfixed32()
        hi = self.sfixed32()
        return decode_int64(lo, hi)

    def float(self):
        value = struct.unpack_from('<f', self.buf, self.pos)[0]
        self.pos += 4
        return value

    def double(self):
        value = struct.unpack_from('<d', self.buf, self.pos)[0]
        self.pos += 8
        return value

    def bytes(self):
        length = self.uint32()
        start = self.pos
        self.pos += length
        self.assert_bounds()
        return self.buf[start:self.pos]

    def string(self):
        return self.decode_utf8(self.bytes())