# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryWriter, BinaryReader


def create_base_format_id():
    return {
        "itag": 0,
        "lastModified": 0,
        "xtags": None
    }

class FormatId:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("itag", 0) != 0:
            writer.uint32(8).int32(message["itag"])

        if message.get("lastModified", 0) != 0:
            writer.uint32(16).uint64(message["lastModified"])

        if message.get("xtags", None) is not None:
            writer.uint32(26).string(message["xtags"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = create_base_format_id()
        while reader.pos < end:
            tag = reader.uint32()
            field_no = tag >> 3

            if field_no == 1 and tag == 8:
                message["itag"] = reader.int32()
                continue
            elif field_no == 2 and tag == 16:
                message["lastModified"] = reader.uint64()
                continue
            elif field_no == 3 and tag == 26:
                message["xtags"] = reader.string()
                continue
            if (tag & 7) == 4 or tag == 0:
                break
            reader.skip(tag & 7)
        return message

class InitRange:
    def __init__(self, start=0, end=0):
        self.start = start
        self.end = end

    @staticmethod
    def encode(message, writer=None):
        if writer is None:
            writer = BinaryWriter()
        if message.start != 0:
            writer.uint32(8)
            writer.int32(message.start)
        if message.end != 0:
            writer.uint32(16)
            writer.int32(message.end)
        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = InitRange()
        while reader.pos < end:
            tag = reader.uint32()
            field_no = tag >> 3
            if field_no == 1 and tag == 8:
                message.start = reader.int32()
                continue
            elif field_no == 2 and tag == 16:
                message.end = reader.int32()
                continue
            if (tag & 7) == 4 or tag == 0:
                break
            reader.skip(tag & 7)
        return message

class IndexRange:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("start", 0) != 0:
            writer.uint32(8).int32(message["start"])

        if message.get("end", 0) != 0:
            writer.uint32(16).int32(message["end"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = {
            "start": 0,
            "end": 0
        }
        while reader.pos < end:
            tag = reader.uint32()
            field_no = tag >> 3
            if field_no == 1 and tag == 8:
                message["start"] = reader.int32()
                continue
            elif field_no == 2 and tag == 16:
                message["end"] = reader.int32()
                continue
            if (tag & 7) == 4 or tag == 0:
                break
            reader.skip(tag & 7)
        return message
