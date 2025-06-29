# All credits to https://github.com/LuanRT/googlevideo

from enum import Enum

from pytubefix.sabr.proto import BinaryReader, BinaryWriter


class StreamProtectionStatus:
    def __init__(self):
        self.status = None
        self.field2 = None

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("status", 0) != 0:
            writer.uint32(8)
            writer.int32(message["status"])
        if message.get("field2") != 0:
            writer.uint32(16)
            writer.int32(message["field2"])
        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = StreamProtectionStatus()

        while reader.pos < end:
            tag = reader.uint32()
            field_no = tag >> 3
            if field_no == 1 and tag == 8:
                message.status = reader.int32()
                continue
            elif field_no == 2 and tag == 16:
                message.field2 = reader.int32()
                continue
            if (tag & 7) == 4 or tag == 0:
                break
            reader.skip(tag & 7)
        return message

    class Status(Enum):
        OK = 1
        ATTESTATION_PENDING = 2
        ATTESTATION_REQUIRED = 3
