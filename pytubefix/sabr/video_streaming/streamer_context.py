# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryWriter, BinaryReader


class StreamerContext_ClientInfo:

    def __init__(self):
        self.deviceMake = "",
        self.deviceModel = "",
        self.clientName = 0,
        self.clientVersion = "",
        self.osName = "",
        self.osVersion = "",
        self.acceptLanguage = "",
        self.acceptRegion = "",
        self.screenWidthPoints = 0,
        self.screenHeightPoints = 0,
        self.screenWidthInches = 0.0,
        self.screenHeightInches = 0.0,
        self.screenPixelDensity = 0,
        self.clientFormFactor = 0,
        self.gmscoreVersionCode = 0,
        self.windowWidthPoints = 0,
        self.windowHeightPoints = 0,
        self.androidSdkVersion = 0,
        self.screenDensityFloat = 0.0,
        self.utcOffsetMinutes = 0,
        self.timeZone = "",
        self.chipset = "",
        self.glDeviceInfo = None,

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("deviceMake", "") != "":
            writer.uint32(98).string(message["deviceMake"])
        if message.get("deviceModel", "") != "":
            writer.uint32(106).string(message["deviceModel"])
        if message.get("clientName", 0) != 0:
            writer.uint32(128).int32(message["clientName"])
        if message.get("clientVersion", "") != "":
            writer.uint32(138).string(message["clientVersion"])
        if message.get("osName", "") != "":
            writer.uint32(146).string(message["osName"])
        if message.get("osVersion", "") != "":
            writer.uint32(154).string(message["osVersion"])
        if message.get("acceptLanguage", "") != "":
            writer.uint32(170).string(message["acceptLanguage"])
        if message.get("acceptRegion", "") != "":
            writer.uint32(178).string(message["acceptRegion"])
        if message.get("screenWidthPoints", 0) != 0:
            writer.uint32(296).int32(message["screenWidthPoints"])
        if message.get("screenHeightPoints", 0) != 0:
            writer.uint32(304).int32(message["screenHeightPoints"])
        if message.get("screenWidthInches", 0) != 0:
            writer.uint32(317).float(message["screenWidthInches"])
        if message.get("screenHeightInches", 0) != 0:
            writer.uint32(325).float(message["screenHeightInches"])
        if message.get("screenPixelDensity", 0) != 0:
            writer.uint32(328).int32(message["screenPixelDensity"])
        if message.get("clientFormFactor", 0) != 0:
            writer.uint32(368).int32(message["clientFormFactor"])
        if message.get("gmscoreVersionCode", 0) != 0:
            writer.uint32(400).int32(message["gmscoreVersionCode"])
        if message.get("windowWidthPoints", 0) != 0:
            writer.uint32(440).int32(message["windowWidthPoints"])
        if message.get("windowHeightPoints", 0) != 0:
            writer.uint32(448).int32(message["windowHeightPoints"])
        if message.get("androidSdkVersion", 0) != 0:
            writer.uint32(512).int32(message["androidSdkVersion"])
        if message.get("screenDensityFloat", 0) != 0:
            writer.uint32(525).float(message["screenDensityFloat"])
        if message.get("utcOffsetMinutes", 0) != 0:
            writer.uint32(536).int64(message["utcOffsetMinutes"])
        if message.get("timeZone", "") != "":
            writer.uint32(642).string(message["timeZone"])
        if message.get("chipset", "") != "":
            writer.uint32(738).string(message["chipset"])

        return writer

    @staticmethod
    def decode_streamer_context_client_info(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext_ClientInfo()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 12 and tag == 98:
                message.deviceMake = reader.string()
            elif field_number == 13 and tag == 106:
                message.deviceModel = reader.string()
            elif field_number == 16 and tag == 128:
                message.clientName = reader.int32()
            elif field_number == 17 and tag == 138:
                message.clientVersion = reader.string()
            elif field_number == 18 and tag == 146:
                message.osName = reader.string()
            elif field_number == 19 and tag == 154:
                message.osVersion = reader.string()
            elif field_number == 21 and tag == 170:
                message.acceptLanguage = reader.string()
            elif field_number == 22 and tag == 178:
                message.acceptRegion = reader.string()
            elif field_number == 37 and tag == 296:
                message.screenWidthPoints = reader.int32()
            elif field_number == 38 and tag == 304:
                message.screenHeightPoints = reader.int32()
            elif field_number == 39 and tag == 317:
                message.screenWidthInches = reader.float()
            elif field_number == 40 and tag == 325:
                message.screenHeightInches = reader.float()
            elif field_number == 41 and tag == 328:
                message.screenPixelDensity = reader.int32()
            elif field_number == 46 and tag == 368:
                message.clientFormFactor = reader.int32()
            elif field_number == 50 and tag == 400:
                message.gmscoreVersionCode = reader.int32()
            elif field_number == 55 and tag == 440:
                message.windowWidthPoints = reader.int32()
            elif field_number == 56 and tag == 448:
                message.windowHeightPoints = reader.int32()
            elif field_number == 64 and tag == 512:
                message.androidSdkVersion = reader.int32()
            elif field_number == 65 and tag == 525:
                message.screenDensityFloat = reader.float()
            elif field_number == 67 and tag == 536:
                message.utcOffsetMinutes = long_to_number(reader.int64())
            elif field_number == 80 and tag == 642:
                message.timeZone = reader.string()
            elif field_number == 92 and tag == 738:
                message.chipset = reader.string()
            else:
                if (tag & 7) == 4 or tag == 0:
                    break
                reader.skip(tag & 7)

        return message


class StreamerContext_Fqa:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("type", 0) != 0:
            writer.uint32(8).int32(message["type"])
        if message.get("value"):
            writer.uint32(18).bytes(message["value"])

        return writer

class StreamerContext_Gqa:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("field1"):
            writer.uint32(10).bytes(message["field1"])
        if message.get("field2") is not None:
            StreamerContext_Gqa_Hqa.encode(message["field2"], writer.uint32(18).fork()).join()

        return writer


class StreamerContext_Gqa_Hqa:
    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("code", 0) != 0:
            writer.uint32(8).int32(message["code"])
        if message.get("message", "") != "":
            writer.uint32(18).string(message["message"])

        return writer


class StreamerContext:

    def __init__(self):
        self.deviceMake = "",
        self.deviceModel = "",
        self.clientName = 0,
        self.clientVersion = "",
        self.osName = "",
        self.osVersion = "",
        self.acceptLanguage = "",
        self.acceptRegion = "",
        self.screenWidthPoints = 0,
        self.screenHeightPoints = 0,
        self.screenWidthInches = 0.0,
        self.screenHeightInches = 0.0,
        self.screenPixelDensity = 0,
        self.clientFormFactor = 0,
        self.gmscoreVersionCode = 0,
        self.windowWidthPoints = 0,
        self.windowHeightPoints = 0,
        self.androidSdkVersion = 0,
        self.screenDensityFloat = 0.0,
        self.utcOffsetMinutes = 0,
        self.timeZone = "",
        self.chipset = "",
        self.glDeviceInfo = None,

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

        for v in message.get("field5", []):
            StreamerContext_Fqa.encode(v, writer.uint32(42).fork()).join()

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
    def decode_streamer_context_client_info(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = StreamerContext()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 12 and tag == 98:
                message.deviceMake = reader.string()
                continue
            if field_number == 13 and tag == 106:
                message.deviceModel = reader.string()
                continue
            if field_number == 16 and tag == 128:
                message.clientName = reader.int32()
                continue
            if field_number == 17 and tag == 138:
                message.clientVersion = reader.string()
                continue
            if field_number == 18 and tag == 146:
                message.osName = reader.string()
                continue
            if field_number == 19 and tag == 154:
                message.osVersion = reader.string()
                continue
            if field_number == 21 and tag == 170:
                message.acceptLanguage = reader.string()
                continue
            if field_number == 22 and tag == 178:
                message.acceptRegion = reader.string()
                continue
            if field_number == 37 and tag == 296:
                message.screenWidthPoints = reader.int32()
                continue
            if field_number == 38 and tag == 304:
                message.screenHeightPoints = reader.int32()
                continue
            if field_number == 39 and tag == 317:
                message.screenWidthInches = reader.float()
                continue
            if field_number == 40 and tag == 325:
                message.screenHeightInches = reader.float()
                continue
            if field_number == 41 and tag == 328:
                message.screenPixelDensity = reader.int32()
                continue
            if field_number == 46 and tag == 368:
                message.clientFormFactor = reader.int32()
                continue
            if field_number == 50 and tag == 400:
                message.gmscoreVersionCode = reader.int32()
                continue
            if field_number == 55 and tag == 440:
                message.windowWidthPoints = reader.int32()
                continue
            if field_number == 56 and tag == 448:
                message.windowHeightPoints = reader.int32()
                continue
            if field_number == 64 and tag == 512:
                message.androidSdkVersion = reader.int32()
                continue
            if field_number == 65 and tag == 525:
                message.screenDensityFloat = reader.float()
                continue
            if field_number == 67 and tag == 536:
                message.utcOffsetMinutes = long_to_number(reader.int64())
                continue
            if field_number == 80 and tag == 642:
                message.timeZone = reader.string()
                continue
            if field_number == 92 and tag == 738:
                message.chipset = reader.string()
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