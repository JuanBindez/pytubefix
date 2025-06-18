# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryReader, BinaryWriter
from pytubefix.sabr.common import FormatId, InitRange, IndexRange


class FormatInitializationMetadata:
    def __init__( self):
        self.videoId = ""
        self.formatId = None
        self.endTimeMs = 0
        self.endSegmentNumber = 0
        self.mimeType = ""
        self.initRange = None
        self.indexRange = None
        self.field8 = 0
        self.durationMs = 0
        self.field10 = 0

    @staticmethod
    def encode(message, writer=None):
        if writer is None:
            writer = BinaryWriter()
        if message.videoId != "":
            writer.uint32(10)
            writer.string(message.videoId)
        if message.formatId is not None:
            writer.uint32(18)
            FormatId.encode(message.formatId, writer.fork()).join()
        if message.endTimeMs != 0:
            writer.uint32(24)
            writer.int32(message.endTimeMs)
        if message.endSegmentNumber != 0:
            writer.uint32(32)
            writer.int64(message.endSegmentNumber)
        if message.mimeType != "":
            writer.uint32(42)
            writer.string(message.mimeType)
        if message.initRange is not None:
            writer.uint32(50)
            InitRange.encode(message.initRange, writer.fork()).join()
        if message.indexRange is not None:
            writer.uint32(58)
            IndexRange.encode(message.indexRange, writer.fork()).join()
        if message.field8 != 0:
            writer.uint32(64)
            writer.int32(message.field8)
        if message.durationMs != 0:
            writer.uint32(72)
            writer.int32(message.durationMs)
        if message.field10 != 0:
            writer.uint32(80)
            writer.int32(message.field10)
        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = FormatInitializationMetadata()
        while reader.pos < end:
            tag = reader.uint32()
            field_no = tag >> 3
            if field_no == 1 and tag == 10:
                message.videoId = reader.string()
                continue
            elif field_no == 2 and tag == 18:
                message.formatId = FormatId.decode(reader, reader.uint32())
                continue
            elif field_no == 3 and tag == 24:
                message.endTimeMs = reader.int32()
                continue
            elif field_no == 4 and tag == 32:
                message.endSegmentNumber = long_to_number(reader.int64())
                continue
            elif field_no == 5 and tag == 42:
                message.mimeType = reader.string()
                continue
            elif field_no == 6 and tag == 50:
                message.initRange = InitRange.decode(reader, reader.uint32())
                continue
            elif field_no == 7 and tag == 58:
                message.indexRange = IndexRange.decode(reader, reader.uint32())
                continue
            elif field_no == 8 and tag == 64:
                message.field8 = reader.int32()
                continue
            elif field_no == 9 and tag == 72:
                message.durationMs = reader.int32()
                continue
            elif field_no == 10 and tag == 80:
                message.field10 = reader.int32()
                continue
            if (tag & 7) == 4 or tag == 0:
                break
            reader.skip(tag & 7)
        return message

def long_to_number(int64_value):
    value = int(str(int64_value))
    if value > (2 ** 53 - 1):
        raise OverflowError("Value is larger than 9007199254740991")
    if value < -(2 ** 53 - 1):
        raise OverflowError("Value is smaller than -9007199254740991")
    return value
