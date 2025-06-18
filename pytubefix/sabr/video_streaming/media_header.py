# All credits to https://github.com/LuanRT/googlevideo

from typing import Optional

from pytubefix.sabr.common import FormatId
from pytubefix.sabr.proto import BinaryReader, BinaryWriter
from pytubefix.sabr.video_streaming.time_range import TimeRange


class MediaHeader:
    def __init__(self):
        self.headerId: int = 0
        self.videoId: str = ""
        self.itag: int = 0
        self.lmt: int = 0
        self.xtags: str = ""
        self.startRange: int = 0
        self.compressionAlgorithm: int = 0
        self.isInitSeg: bool = False
        self.sequenceNumber: int = 0
        self.field10: int = 0
        self.startMs: int = 0
        self.durationMs: int = 0
        self.formatId: Optional[FormatId] = None
        self.contentLength: int = 0
        self.timeRange: Optional[TimeRange] = None

    @staticmethod
    def decode(reader, length: Optional[int] = None):
        if not isinstance(reader, BinaryReader) :
            reader = BinaryReader(reader)
        end = reader.len if length is None else reader.pos + length
        message = MediaHeader()
        while reader.pos < end:
            tag = reader.uint32()
            field = tag >> 3

            if field == 1 and tag == 8:
                message.headerId = reader.uint32()
                continue
            elif field == 2 and tag == 18:
                message.videoId = reader.string()
                continue
            elif field == 3 and tag == 24:
                message.itag = reader.int32()
                continue
            elif field == 4 and tag == 32:
                message.lmt = long_to_number(reader.uint64())
                continue
            elif field == 5 and tag == 42:
                message.xtags = reader.string()
                continue
            elif field == 6 and tag == 48:
                message.startRange = long_to_number(reader.int64())
                continue
            elif field == 7 and tag == 56:
                message.compressionAlgorithm = reader.int32()
                continue
            elif field == 8 and tag == 64:
                message.isInitSeg = reader.bool()
                continue
            elif field == 9 and tag == 72:
                message.sequenceNumber = long_to_number(reader.int64())
                continue
            elif field == 10 and tag == 80:
                message.field10 = long_to_number(reader.int64())
                continue
            elif field == 11 and tag == 88:
                message.startMs = long_to_number(reader.int64())
                continue
            elif field == 12 and tag == 96:
                message.durationMs = long_to_number(reader.int64())
                continue
            elif field == 13 and tag == 106:
                length = reader.uint32()
                message.formatId = FormatId.decode(reader, length)
                continue
            elif field == 14 and tag == 112:
                message.contentLength = long_to_number(reader.int64())
                continue
            elif field == 15 and tag == 122:
                length = reader.uint32()
                message.timeRange = TimeRange.decode(reader, length)
                continue
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)
        return message

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("headerId", 0):
            writer.uint32(8).uint32(message["headerId"])
        if message.get("videoId", ""):
            writer.uint32(18).string(message["videoId"])
        if message.get("itag", 0):
            writer.uint32(24).int32(message["itag"])
        if message.get("lmt", 0):
            writer.uint32(32).uint64(message["lmt"])
        if message.get("xtags", ""):
            writer.uint32(42).string(message["xtags"])
        if message.get("startRange", 0):
            writer.uint32(48).int64(message["startRange"])
        if message.get("compressionAlgorithm", 0):
            writer.uint32(56).int32(message["compressionAlgorithm"])
        if message.get("isInitSeg", False):
            writer.uint32(64).bool(message["isInitSeg"])
        if message.get("sequenceNumber", 0):
            writer.uint32(72).int64(message["sequenceNumber"])
        if message.get("field10", 0):
            writer.uint32(80).int64(message["field10"])
        if message.get("startMs", 0):
            writer.uint32(88).int64(message["startMs"])
        if message.get("durationMs", 0):
            writer.uint32(96).int64(message["durationMs"])
        if message.get("formatId", 0):
            FormatId.encode(message["formatId"], writer.uint32(106).fork()).join()
        if message.get("contentLength", 0):
            writer.uint32(112).int64(message["contentLength"])
        if message.get("timeRange", 0):
            TimeRange.encode(message["timeRange"], writer.uint32(122).fork()).join()

        return writer

def long_to_number(int64_value):
    value = int(str(int64_value))
    if value > (2 ** 53 - 1):
        raise OverflowError("Value is larger than 9007199254740991")
    if value < -(2 ** 53 - 1):
        raise OverflowError("Value is smaller than -9007199254740991")
    return value