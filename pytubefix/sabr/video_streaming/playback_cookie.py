# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.common import FormatId
from pytubefix.sabr.proto import BinaryReader, BinaryWriter


class PlaybackCookie:
    @staticmethod
    def create_base():
        return {
            "field1": 0,
            "field2": 0,
            "videoFmt": None,
            "audioFmt": None
        }

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("field1", 0) != 0:
            writer.uint32(8).int32(message["field1"])

        if message.get("field2", 0) != 0:
            writer.uint32(16).int32(message["field2"])

        if message.get("videoFmt") is not None:
            FormatId.encode(message["videoFmt"], writer.uint32(58).fork()).join()

        if message.get("audioFmt") is not None:
            FormatId.encode(message["audioFmt"], writer.uint32(66).fork()).join()

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = PlaybackCookie.create_base()

        while reader.pos < end:
            tag = reader.uint32()
            field = tag >> 3

            if field == 1 and tag == 8:
                message["field1"] = reader.int32()
                continue
            elif field == 2 and tag == 16:
                message["field2"] = reader.int32()
                continue
            elif field == 7 and tag == 58:
                message["videoFmt"] = FormatId.decode(reader, reader.uint32())
                continue
            elif field == 8 and tag == 66:
                message["audioFmt"] = FormatId.decode(reader, reader.uint32())
                continue
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message
