# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.common import FormatId
from pytubefix.sabr.proto import BinaryWriter, BinaryReader
from pytubefix.sabr.video_streaming.time_range import TimeRange


def create_base_buffered_range():
    return {
        "formatId": None,
        "startTimeMs": 0,
        "durationMs": 0,
        "startSegmentIndex": 0,
        "endSegmentIndex": 0,
        "timeRange": None,
        "field9": None,
        "field11": None,
        "field12": None
    }


def create_base_kob():
    return {"EW": []}


def create_base_kob_pa():
    return {"videoId": "", "lmt": 0}


def create_base_ypa():
    return {"field1": 0, "field2": 0, "field3": 0}


class Kob_Pa:
    @staticmethod
    def encode(message, writer=None):
        writer = writer or BinaryWriter()
        if message.get("videoId"):
            writer.uint32(10).string(message["videoId"])
        if message.get("lmt", 0) != 0:
            writer.uint32(16).uint64(message["lmt"])
        return writer

    @staticmethod
    def decode(reader, length):
        end = reader.pos + length if length is not None else reader.len
        message = create_base_kob_pa()
        while reader.pos < end:
            tag = reader.uint32()
            if tag == 10:
                message["videoId"] = reader.string()
            elif tag == 16:
                message["lmt"] = long_to_number(reader.uint64())
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)
        return message


class Kob:
    @staticmethod
    def encode(message, writer=None):
        writer = writer or BinaryWriter()
        for v in message.get("EW", []):
            Kob_Pa.encode(v, writer.uint32(10).fork()).join()
        return writer

    @staticmethod
    def decode(reader, length):
        end = reader.pos + length if length is not None else reader.len
        message = create_base_kob()
        while reader.pos < end:
            tag = reader.uint32()
            if tag == 10:
                message["EW"].append(Kob_Pa.decode(reader, reader.uint32()))
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)
        return message


class YPa:
    @staticmethod
    def encode(message, writer=None):
        writer = writer or BinaryWriter()
        if message.get("field1", 0) != 0:
            writer.uint32(8).int32(message["field1"])
        if message.get("field2", 0) != 0:
            writer.uint32(16).int32(message["field2"])
        if message.get("field3", 0) != 0:
            writer.uint32(24).int32(message["field3"])
        return writer

    @staticmethod
    def decode(reader, length):
        end = reader.pos + length if length is not None else reader.len
        message = create_base_ypa()
        while reader.pos < end:
            tag = reader.uint32()
            if tag == 8:
                message["field1"] = reader.int32()
            elif tag == 16:
                message["field2"] = reader.int32()
            elif tag == 24:
                message["field3"] = reader.int32()
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)
        return message


class BufferedRange:
    @staticmethod
    def encode(message, writer=None):
        writer = writer or BinaryWriter()
        if message.get("formatId") is not None:
            FormatId.encode(message["formatId"], writer.uint32(10).fork()).join()
        if message.get("startTimeMs", 0) != 0:
            writer.uint32(16).int64(message["startTimeMs"])
        if message.get("durationMs", 0) != 0:
            writer.uint32(24).int64(message["durationMs"])
        if message.get("startSegmentIndex", 0) != 0:
            writer.uint32(32).int32(message["startSegmentIndex"])
        if message.get("endSegmentIndex", 0) != 0:
            writer.uint32(40).int32(message["endSegmentIndex"])
        if message.get("timeRange") is not None:
            TimeRange.encode(message["timeRange"], writer.uint32(50).fork()).join()
        if message.get("field9") is not None:
            Kob.encode(message["field9"], writer.uint32(74).fork()).join()
        if message.get("field11") is not None:
            YPa.encode(message["field11"], writer.uint32(90).fork()).join()
        if message.get("field12") is not None:
            YPa.encode(message["field12"], writer.uint32(98).fork()).join()
        return writer

    @staticmethod
    def decode(reader, length):
        if not isinstance(reader, BinaryReader):
            reader = BinaryReader(reader)
        end = reader.pos + length if length is not None else reader.len
        message = create_base_buffered_range()
        while reader.pos < end:
            tag = reader.uint32()
            field_num = tag >> 3
            if field_num == 1 and tag == 10:
                message["formatId"] = FormatId.decode(reader, reader.uint32())
            elif field_num == 2 and tag == 16:
                message["startTimeMs"] = long_to_number(reader.int64())
            elif field_num == 3 and tag == 24:
                message["durationMs"] = long_to_number(reader.int64())
            elif field_num == 4 and tag == 32:
                message["startSegmentIndex"] = reader.int32()
            elif field_num == 5 and tag == 40:
                message["endSegmentIndex"] = reader.int32()
            elif field_num == 6 and tag == 50:
                message["timeRange"] = TimeRange.decode(reader, reader.uint32())
            elif field_num == 9 and tag == 74:
                message["field9"] = Kob.decode(reader, reader.uint32())
            elif field_num == 11 and tag == 90:
                message["field11"] = YPa.decode(reader, reader.uint32())
            elif field_num == 12 and tag == 98:
                message["field12"] = YPa.decode(reader, reader.uint32())
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)
        return message

def long_to_number(int64_value):
    value = int(str(int64_value))
    if value > (2 ** 53 - 1):
        raise OverflowError("Value is larger than 9007199254740991")
    if value < -(2 ** 53 - 1):
        raise OverflowError("Value is smaller than -9007199254740991")
    return value
