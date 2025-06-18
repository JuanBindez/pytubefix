# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryReader, BinaryWriter


class SabrRedirect:

    def __init__(self):
        self.url = ""

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("url") not in (None, ""):
            writer.uint32(10).string(message["url"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length

        message = SabrRedirect

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.url = reader.string()
                continue

            if (tag & 7) == 4 or tag == 0:
                break

            reader.skip(tag & 7)

        return message
