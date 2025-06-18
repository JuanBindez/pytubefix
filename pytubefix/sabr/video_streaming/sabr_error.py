# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryWriter, BinaryReader


class SabrError:

    def __init__(self):
        self.type = ""
        self.code = 0

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("type") not in (None, ""):
            writer.uint32(10).string(message["type"])
        if message.get("code") not in (None, 0):
            writer.uint32(16).int32(message["code"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length

        message = SabrError()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.type = reader.string()
                continue
            if field_number == 2 and tag == 16:
                message.code = reader.int32()
                continue

            if (tag & 7) == 4 or tag == 0:
                break
            reader.skip(tag & 7)

        return message
