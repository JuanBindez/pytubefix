# All credits to https://github.com/LuanRT/googlevideo
from enum import Enum

from pytubefix.sabr.proto import BinaryWriter, BinaryReader
from pytubefix.sabr.video_streaming.playback_cookie import PlaybackCookie


class StreamerContext_ClientInfo:

    def __init__(self):
        self.locale = None
        self.deviceMake = None
        self.deviceModel = None
        self.clientName = None
        self.clientVersion = None
        self.osName = None
        self.osVersion = None
        self.acceptLanguage = None
        self.acceptRegion = None
        self.screenWidthPoints = None
        self.screenHeightPoints = None
        self.screenWidthInches = None
        self.screenHeightInches = None
        self.screenPixelDensity = None
        self.clientFormFactor = None
        self.gmscoreVersionCode = None
        self.windowWidthPoints = None
        self.windowHeightPoints = None
        self.androidSdkVersion = None
        self.screenDensityFloat = None
        self.utcOffsetMinutes = None
        self.timeZone = None
        self.chipset = None
        self.glDeviceInfo = None

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("deviceMake", ""):
            writer.uint32(98).string(message["deviceMake"])
        if message.get("deviceModel", "") :
            writer.uint32(106).string(message["deviceModel"])
        if message.get("clientName", 0):
            writer.uint32(128).int32(message["clientName"])
        if message.get("clientVersion", ""):
            writer.uint32(138).string(message["clientVersion"])
        if message.get("osName", ""):
            writer.uint32(146).string(message["osName"])
        if message.get("osVersion", ""):
            writer.uint32(154).string(message["osVersion"])
        if message.get("acceptLanguage", ""):
            writer.uint32(170).string(message["acceptLanguage"])
        if message.get("acceptRegion", ""):
            writer.uint32(178).string(message["acceptRegion"])
        if message.get("screenWidthPoints", 0):
            writer.uint32(296).int32(message["screenWidthPoints"])
        if message.get("screenHeightPoints", 0):
            writer.uint32(304).int32(message["screenHeightPoints"])
        if message.get("screenWidthInches", 0):
            writer.uint32(317).float(message["screenWidthInches"])
        if message.get("screenHeightInches", 0):
            writer.uint32(325).float(message["screenHeightInches"])
        if message.get("screenPixelDensity", 0):
            writer.uint32(328).int32(message["screenPixelDensity"])
        if message.get("clientFormFactor", 0):
            writer.uint32(368).int32(message["clientFormFactor"])
        if message.get("gmscoreVersionCode", 0):
            writer.uint32(400).int32(message["gmscoreVersionCode"])
        if message.get("windowWidthPoints", 0):
            writer.uint32(440).int32(message["windowWidthPoints"])
        if message.get("windowHeightPoints", 0):
            writer.uint32(448).int32(message["windowHeightPoints"])
        if message.get("androidSdkVersion", 0):
            writer.uint32(512).int32(message["androidSdkVersion"])
        if message.get("screenDensityFloat", 0):
            writer.uint32(525).float(message["screenDensityFloat"])
        if message.get("utcOffsetMinutes", 0):
            writer.uint32(536).int64(message["utcOffsetMinutes"])
        if message.get("timeZone", ""):
            writer.uint32(642).string(message["timeZone"])
        if message.get("chipset", ""):
            writer.uint32(738).string(message["chipset"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext_ClientInfo()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.locale = reader.string()
                continue
            if field_number == 12 and tag == 98:
                message.deviceMake = reader.string()
                continue
            elif field_number == 13 and tag == 106:
                message.deviceModel = reader.string()
                continue
            elif field_number == 16 and tag == 128:
                message.clientName = reader.int32()
                continue
            elif field_number == 17 and tag == 138:
                message.clientVersion = reader.string()
                continue
            elif field_number == 18 and tag == 146:
                message.osName = reader.string()
                continue
            elif field_number == 19 and tag == 154:
                message.osVersion = reader.string()
                continue
            elif field_number == 21 and tag == 170:
                message.acceptLanguage = reader.string()
                continue
            elif field_number == 22 and tag == 178:
                message.acceptRegion = reader.string()
                continue
            elif field_number == 37 and tag == 296:
                message.screenWidthPoints = reader.int32()
                continue
            elif field_number == 38 and tag == 304:
                message.screenHeightPoints = reader.int32()
                continue
            elif field_number == 39 and tag == 317:
                message.screenWidthInches = reader.float()
                continue
            elif field_number == 40 and tag == 325:
                message.screenHeightInches = reader.float()
                continue
            elif field_number == 41 and tag == 328:
                message.screenPixelDensity = reader.int32()
                continue
            elif field_number == 46 and tag == 368:
                message.clientFormFactor = reader.int32()
                continue
            elif field_number == 50 and tag == 400:
                message.gmscoreVersionCode = reader.int32()
                continue
            elif field_number == 55 and tag == 440:
                message.windowWidthPoints = reader.int32()
                continue
            elif field_number == 56 and tag == 448:
                message.windowHeightPoints = reader.int32()
                continue
            elif field_number == 64 and tag == 512:
                message.androidSdkVersion = reader.int32()
                continue
            elif field_number == 65 and tag == 525:
                message.screenDensityFloat = reader.float()
                continue
            elif field_number == 67 and tag == 536:
                message.utcOffsetMinutes = long_to_number(reader.int64())
                continue
            elif field_number == 80 and tag == 642:
                message.timeZone = reader.string()
                continue
            elif field_number == 92 and tag == 738:
                message.chipset = reader.string()
                continue
            elif field_number == 102 and tag == 818:
                message.glDeviceInfo = StreamerContext_GLDeviceInfo.decode(reader, reader.uint32())
            else:
                if (tag & 7) == 4 or tag == 0:
                    break
                reader.skip(tag & 7)

        return message


class StreamerContext_GLDeviceInfo:

    def __init__(self):
        self.glRenderer = ""
        self.glEsVersionMajor = 0
        self.glEsVersionMinor = 0

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("glRenderer", ""):
            writer.uint32(10).string(message["glRenderer"])
        if message.get("glEsVersionMajor", ""):
            writer.uint32(16).int32(message["glEsVersionMajor"])
        if message.get("glEsVersionMinor", ""):
            writer.uint32(24).int32(message["glEsVersionMinor"])

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext_GLDeviceInfo()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.glRenderer = reader.string()
                continue
            elif field_number == 2 and tag == 16:
                message.glEsVersionMajor = reader.int32()
                continue
            elif field_number == 3 and tag == 24:
                message.glEsVersionMinor = reader.int32()
                continue

            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message

class StreamerContextUpdate:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("type", 0):
            writer.uint32(8).int32(message["type"])

        if message.get("value", 0):
            StreamerContextUpdateValue.encode(message["value"], writer.uint32(18).fork()).join()

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = dict()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 8:
                message["type"] = reader.int32()
                continue
            elif field_number == 2 and tag == 16:
                message["scope"] = reader.int32()
                continue
            elif field_number == 3 and tag == 26:
                message["value"] = StreamerContextUpdateValue.decode(reader, reader.uint32())
                continue
            elif field_number == 4 and tag == 32:
                message["sendByDefault"] = reader.bool()
                continue
            elif field_number == 5 and tag == 40:
                message["writePolicy"] = reader.int32()
                continue

            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message

    class SabrContextWritePolicy(Enum):
        SABR_CONTEXT_WRITE_POLICY_UNSPECIFIED = 0
        SABR_CONTEXT_WRITE_POLICY_OVERWRITE = 1
        SABR_CONTEXT_WRITE_POLICY_KEEP_EXISTING = 2

class StreamerContextUpdateValue:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("field1", 0):
            StreamerContextUpdateField1.encode(message["field1"], writer.uint32(10).fork()).join()
        if message.get("field2", 0):
            writer.uint32(18).bytes(message["field2"])
        if message.get("field3", 0):
            writer.uint32(40).int32(message["field3"])

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = dict()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message["field1"] = StreamerContextUpdateField1.decode(reader, reader.uint32())
                continue
            elif field_number == 2 and tag == 18:
                message["field2"] = reader.bytes()
                continue
            elif field_number == 5 and tag == 40:
                message["field3"] = reader.int32()
                continue

            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message

class StreamerContextUpdateField1:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("timestamp", 0):
            writer.uint32(8).int64(message["timestamp"])
        if message.get("skip", 0):
            writer.uint32(16).int32(message["skip"])
        if message.get("fiedl3", 0):
            writer.uint32(26).bytes(message["fiedl3"])

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = dict()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 8:
                message["timestamp"] = reader.int64()
                continue
            elif field_number == 2 and tag == 16:
                message["skip"] = reader.int32()
                continue
            elif field_number == 3 and tag == 26:
                message["fiedl3"] = reader.bytes()
                continue

            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message


class StreamerContext_Gqa:

    def __init__(self):
        self.field1 = None
        self.field2 = None

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("field1", 0):
            writer.uint32(10).bytes(message["field1"])
        if message.get("field2", 0):
            StreamerContext_Gqa_Hqa.encode(message["field2"], writer.uint32(18).fork()).join()

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext_Gqa()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.field1 = reader.bytes()
                continue
            elif field_number == 2 and tag == 18:
                message.field2 = StreamerContext_Gqa_Hqa.decode(reader, reader.uint32())
                continue

            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message


class StreamerContext_Gqa_Hqa:

    def __init__(self):
        self.code = 0
        self.message = ""

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("code", 0):
            writer.uint32(8).int32(message["code"])
        if message.get("message", ""):
            writer.uint32(18).string(message["message"])

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext_Gqa_Hqa()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 8:
                message.code = reader.int32()
                continue
            elif field_number == 2 and tag == 18:
                message.message = reader.string()
                continue

            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message


class StreamerContext:

    def __init__(self):
        self.clientInfo = None
        self.poToken = None
        self.playbackCookie = None
        self.gp = None
        self.sabrContexts = []
        self.field6 = []
        self.field6 = ""
        self.field6 = []


    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("clientInfo") is not None:
            StreamerContext_ClientInfo.encode(message["clientInfo"], writer.uint32(10).fork()).join()

        if message.get("poToken"):
            writer.uint32(18).bytes(message["poToken"])

        if message.get("playbackCookie"):
            writer.uint32(26).bytes(message["playbackCookie"])

        if message.get("gp"):
            writer.uint32(34).bytes(message["gp"])

        for v in message.get("sabrContexts", []):
            StreamerContextUpdate.encode(v, writer.uint32(42).fork()).join()

        writer.uint32(50).fork()
        for v in message.get("field6", []):
            writer.int32(v)
        writer.join()

        if message.get("field7", "") != "":
            writer.uint32(58).string(message["field7"])

        if message.get("field8") is not None:
            StreamerContext_Gqa.encode(message["field8"], writer.uint32(66).fork()).join()

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.clientInfo = StreamerContext_ClientInfo.decode(reader, reader.uint32())
                continue
            if field_number == 2 and tag == 18:
                message.poToken = reader.bytes()
                continue
            if field_number == 3 and tag == 26:
                message.playbackCookie = PlaybackCookie.decode(reader, reader.uint32())
                continue
            if field_number == 4 and tag == 34:
                message.gp = reader.bytes()
                continue
            if field_number == 5 and tag == 42:
                message.sabrContexts.append(StreamerContextUpdate.decode(reader, reader.uint32())) # sabrContexts
                continue
            if field_number == 6 and tag == 48:
                message.field6.append(reader.int32()) # unsentSabrContexts
                continue
            if field_number == 6 and tag == 50:
                end2 = reader.uint32() + reader.pos
                while (reader.pos < end2):
                    message.field6.append(reader.int32())
                continue
            if field_number == 7 and tag == 58:
                message.field7 = reader.string()
                continue
            if field_number == 8 and tag == 66:
                message.field5.append(StreamerContext_Gqa.decode(reader, reader.uint32()))
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