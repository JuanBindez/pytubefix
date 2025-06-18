# All credits to https://github.com/LuanRT/googlevideo

from typing import List, Optional

from pytubefix.sabr.common import FormatId
from pytubefix.sabr.proto import BinaryWriter, BinaryReader
from pytubefix.sabr.video_streaming.buffered_range import BufferedRange
from pytubefix.sabr.video_streaming.client_abr_state import ClientAbrState
from pytubefix.sabr.video_streaming.streamer_context import StreamerContext


class VideoPlaybackAbrRequest:
    def __init__(self):
        self.client_abr_state: Optional[ClientAbrState] = None
        self.selected_format_ids: List[FormatId] = []
        self.buffered_ranges: List[BufferedRange] = []
        self.player_time_ms: int = 0
        self.video_playback_ustreamer_config: bytes = bytes()
        self.lo = None
        self.lj = None
        self.selected_audio_format_ids: List[FormatId] = []
        self.selected_video_format_ids: List[FormatId] = []
        self.streamer_context: Optional[StreamerContext] = None
        self.field1 = None
        self.field2 = None
        self.field3 = None
        self.field21: Optional[OQa] = None
        self.field22: int = 0
        self.field23: int = 0
        self.field1000: List[Pqa] = []

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if "clientAbrState" in message and message["clientAbrState"] is not None:
            writer.uint32(10)
            ClientAbrState.encode(message["clientAbrState"], writer.fork())
            writer.join()

        for v in message.get("selectedFormatIds", []):
            writer.uint32(18)
            FormatId.encode(v, writer.fork())
            writer.join()

        for v in message.get("bufferedRanges", []):
            writer.uint32(26)
            BufferedRange.encode(v, writer.fork())
            writer.join()

        if message.get("playerTimeMs", 0):
            writer.uint32(32).int64(message["playerTimeMs"])

        if message.get("videoPlaybackUstreamerConfig", b''):
            writer.uint32(42).bytes(message["videoPlaybackUstreamerConfig"])

        if "lo" in message and message["lo"] is not None:
            writer.uint32(50)
            Lo.encode(message["lo"], writer.fork())
            writer.join()

        for v in message.get("selectedAudioFormatIds", []):
            writer.uint32(130)
            FormatId.encode(v, writer.fork())
            writer.join()

        for v in message.get("selectedVideoFormatIds", []):
            writer.uint32(138)
            FormatId.encode(v, writer.fork())
            writer.join()

        if "streamerContext" in message and message["streamerContext"] is not None:
            writer.uint32(154)
            StreamerContext.encode(message["streamerContext"], writer.fork())
            writer.join()

        if "field21" in message and message["field21"] is not None:
            writer.uint32(170)
            OQa.encode(message["field21"], writer.fork())
            writer.join()

        if message.get("field22", 0):
            writer.uint32(176).int32(message["field22"])

        if message.get("field23", 0):
            writer.uint32(184).int32(message["field23"])

        for v in message.get("field1000", []):
            writer.uint32(8002)
            Pqa.encode(v, writer.fork())
            writer.join()

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = VideoPlaybackAbrRequest()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.client_abr_state = ClientAbrState.decode(reader, reader.uint32())
                continue
            elif field_number == 2 and tag == 18:
                message.selected_format_ids.append(FormatId.decode(reader, reader.uint32()))
                continue
            elif field_number == 3 and tag == 26:
                message.buffered_ranges.append(BufferedRange.decode(reader, reader.uint32()))
                continue
            elif field_number == 4 and tag == 32:
                message.player_time_ms = long_to_number(reader.int64())
                continue
            elif field_number == 5 and tag == 42:
                message.video_playback_ustreamer_config = reader.bytes()
                continue
            elif field_number == 6 and tag == 50:
                message.lo = Lo.decode(reader, reader.uint32())
                continue
            elif field_number == 16 and tag == 130:
                message.selected_audio_format_ids.append(FormatId.decode(reader, reader.uint32()))
                continue
            elif field_number == 17 and tag == 138:
                message.selected_video_format_ids.append(FormatId.decode(reader, reader.uint32()))
                continue
            elif field_number == 19 and tag == 154:
                message.streamer_context = StreamerContext.decode(reader, reader.uint32())
                continue
            elif field_number == 21 and tag == 170:
                message.field21 = OQa.decode(reader, reader.uint32())
                continue
            elif field_number == 22 and tag == 176:
                message.field22 = reader.int32()
                continue
            elif field_number == 23 and tag == 184:
                message.field23 = reader.int32()
                continue
            elif field_number == 1000 and tag == 8002:
                message.field1000.append(Pqa.decode(reader, reader.uint32()))
                continue


        return message


class Lo:
    def __init__(self):
        self.format_id: Optional[FormatId] = None
        self.Lj: int = 0
        self.sequence_number: int = 0
        self.field4: Optional[Lo_Field4] = None
        self.MZ: int = 0

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        for v in message.get("field1", []):
            writer.uint32(10).string(v)

        if "field2" in message and message["field2"] is not None:
            writer.uint32(18).int32(message["field2"])

        if "field3" in message and message["field3"] is not None:
            writer.uint32(26).int32(message["field3"])

        if "field4" in message and message["field4"] is not None:
            writer.uint32(32).int32(message["field4"])

        if "field5" in message and message["field5"] is not None:
            writer.uint32(40).int32(message["field5"])

        if "field6" in message and message["field6"] is not None:
            writer.uint32(50).int32(message["field6"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = Lo()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.format_id = FormatId.decode(reader, reader.uint32())
                continue
            elif field_number == 2 and tag == 16:
                message.Lj = reader.int32()
                continue
            elif field_number == 3 and tag == 24:
                message.sequenceNumber = reader.int32()
                continue
            elif field_number == 4 and tag == 34:
                message.field4 = Lo_Field4.decode(reader, reader.uint32())
                continue
            elif field_number == 5 and tag == 40:
                message.MZ = reader.int32()
                continue

        return message


class Lo_Field4:
    def __init__(self):
        self.field1: int = 0
        self.field2: int = 0
        self.field3: int = 0

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if "field1" in message and message["field1"] is not None:
            writer.uint32(8).int32(message["field1"])

        if "field2" in message and message["field2"] is not None:
            writer.uint32(16).int32(message["field2"])

        if "field3" in message and message["field3"] is not None:
            writer.uint32(24).int32(message["field3"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = Lo_Field4()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3  # Varint

            if field_number == 1 and tag == 8:
                message.field1 = reader.int32()
                continue
            elif field_number == 2 and tag == 16:
                message.field2 = reader.int32()
                continue
            elif field_number == 3 and tag == 24:
                message.field3 = reader.int32()
                continue

        return message


class OQa:
    def __init__(self):
        self.field1: List[str] = []
        self.field2: bytes = bytes()
        self.field3: str = ""
        self.field4: int = 0
        self.field5: int = 0
        self.field6: str = ""

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if "field1" in message and message["field1"] is not None:
            writer.uint32(8).int32(message["field1"])

        if "field2" in message and message["field2"] is not None:
            writer.uint32(16).int32(message["field2"])

        if "field3" in message and message["field3"] is not None:
            writer.uint32(24).int32(message["field3"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = OQa()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.field1.append(reader.string())
                continue
            elif field_number == 2 and tag == 18:
                message.field2 = reader.bytes()
                continue
            elif field_number == 3 and tag == 26:
                message.field3 = reader.string()
                continue
            elif field_number == 4 and tag == 32:
                message.field4 = reader.int32()
                continue
            elif field_number == 5 and tag == 40:
                message.field5 = reader.int32()
                continue
            elif field_number == 6 and tag == 50:
                message.field6 = reader.string()
                continue

        return message


class Pqa:
    def __init__(self):
        self.formats: List[FormatId] = []
        self.ud: List[BufferedRange] = []
        self.clip_id: str = ""

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        for v in message.get("formats", []):
            FormatId.encode(v, writer.uint32(10).fork()).join()

        for v in message.get("ud", []):
            BufferedRange.encode(v, writer.uint32(18).fork()).join()

        if "clipId" in message and message["clipId"] is not None:
            writer.uint32(26).int32(message["clipId"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        message = Pqa()
        end = reader.len if length is None else reader.pos + length

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 1 and tag == 10:
                message.formats.append(FormatId.decode(reader, reader.uint32()))
                continue
            elif field_number == 2 and tag == 18:
                message.ud.append(BufferedRange.decode(reader, reader.uint32()))
                continue
            elif field_number == 3 and tag == 26:
                message.clip_id = reader.string()
                continue

        return message

def long_to_number(int64_value):
    value = int(str(int64_value))
    if value > (2 ** 53 - 1):
        raise OverflowError("Value is larger than 9007199254740991")
    if value < -(2 ** 53 - 1):
        raise OverflowError("Value is smaller than -9007199254740991")
    return value