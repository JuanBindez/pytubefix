# All credits to https://github.com/LuanRT/googlevideo

from typing import Optional

from pytubefix.sabr.proto import BinaryReader, BinaryWriter


class TimeRange:
    def __init__(self):
        self.start: int = 0
        self.duration: int = 0
        self.timescale: int = 0

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = TimeRange

        while reader.pos < end:
            tag = reader.uint32()
            field = tag >> 3

            if field == 1 and tag == 8:
                message.start = long_to_number(reader.int64())
                continue
            elif field == 2 and tag == 16:
                message.duration = long_to_number(reader.int64())
                continue
            elif field == 3 and tag == 24:
                message.timescale = reader.int32()
                continue
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message

    def encode(self, writer: Optional[BinaryWriter] = None) -> BinaryWriter:
        writer = writer or BinaryWriter()

        if self.start != 0:
            writer.uint32(8).int64(self.start)
        if self.duration != 0:
            writer.uint32(16).int64(self.duration)
        if self.timescale != 0:
            writer.uint32(24).int32(self.timescale)
        return writer

def long_to_number(int64_value):
    value = int(str(int64_value))
    if value > (2 ** 53 - 1):
        raise OverflowError("Value is larger than 9007199254740991")
    if value < -(2 ** 53 - 1):
        raise OverflowError("Value is smaller than -9007199254740991")
    return value