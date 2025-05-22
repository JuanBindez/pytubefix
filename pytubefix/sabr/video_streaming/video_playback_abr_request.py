# All credits to https://github.com/LuanRT/googlevideo

import struct
from typing import List, Optional

from pytubefix.sabr.common import FormatId
from pytubefix.sabr.proto import BinaryWriter
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
        self.lo: Optional[Lo] = None
        self.selected_audio_format_ids: List[FormatId] = []
        self.selected_video_format_ids: List[FormatId] = []
        self.streamer_context: Optional[StreamerContext] = None
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
    def decode(data):
        message = VideoPlaybackAbrRequest()
        pos = 0

        while pos < len(data):
            field_number, wire_type = struct.unpack('>BB', data[pos:pos + 2])
            pos += 2

            if wire_type == 2:  # Length-delimited
                length = struct.unpack('>I', data[pos:pos + 4])[0]
                pos += 4
                field_data = data[pos:pos + length]
                pos += length

                if field_number == 1:
                    message.client_abr_state = ClientAbrState.decode(field_data)
                elif field_number == 2:
                    message.selected_format_ids.append(FormatId.decode(field_data))
                elif field_number == 3:
                    message.buffered_ranges.append(BufferedRange.decode(field_data))
                elif field_number == 5:
                    message.video_playback_ustreamer_config = field_data
                elif field_number == 6:
                    message.lo = Lo.decode(field_data)
                elif field_number == 16:
                    message.selected_audio_format_ids.append(FormatId.decode(field_data))
                elif field_number == 17:
                    message.selected_video_format_ids.append(FormatId.decode(field_data))
                elif field_number == 19:
                    message.streamer_context = StreamerContext.decode(field_data)
                elif field_number == 21:
                    message.field21 = OQa.decode(field_data)
                elif field_number == 1000:
                    message.field1000.append(Pqa.decode(field_data))

            elif wire_type == 0:  # Varint
                if field_number == 4:
                    message.player_time_ms = struct.unpack('>Q', data[pos:pos + 8])[0]
                    pos += 8
                elif field_number == 22:
                    message.field22 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4
                elif field_number == 23:
                    message.field23 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4

        return message


class Lo:
    def __init__(self):
        self.format_id: Optional[FormatId] = None
        self.lj: int = 0
        self.sequence_number: int = 0
        self.field4: Optional[Lo_Field4] = None
        self.mz: int = 0

    @staticmethod
    def encode(message):
        data = bytearray()

        if message.format_id is not None:
            data.extend(struct.pack('>B', 10))
            format_id_data = FormatId.encode(message.format_id)
            data.extend(struct.pack('>I', len(format_id_data)))
            data.extend(format_id_data)

        if message.lj != 0:
            data.extend(struct.pack('>Bi', 16, message.lj))

        if message.sequence_number != 0:
            data.extend(struct.pack('>Bi', 24, message.sequence_number))

        if message.field4 is not None:
            data.extend(struct.pack('>B', 34))
            field4_data = Lo_Field4.encode(message.field4)
            data.extend(struct.pack('>I', len(field4_data)))
            data.extend(field4_data)

        if message.mz != 0:
            data.extend(struct.pack('>Bi', 40, message.mz))

        return bytes(data)

    @staticmethod
    def decode(data):
        message = Lo()
        pos = 0

        while pos < len(data):
            field_number, wire_type = struct.unpack('>BB', data[pos:pos + 2])
            pos += 2

            if wire_type == 2:  # Length-delimited
                length = struct.unpack('>I', data[pos:pos + 4])[0]
                pos += 4
                field_data = data[pos:pos + length]
                pos += length

                if field_number == 1:
                    message.format_id = FormatId.decode(field_data)
                elif field_number == 4:
                    message.field4 = Lo_Field4.decode(field_data)

            elif wire_type == 0:  # Varint
                if field_number == 2:
                    message.lj = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4
                elif field_number == 3:
                    message.sequence_number = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4
                elif field_number == 5:
                    message.mz = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4

        return message


class Lo_Field4:
    def __init__(self):
        self.field1: int = 0
        self.field2: int = 0
        self.field3: int = 0

    @staticmethod
    def encode(message):
        data = bytearray()

        if message.field1 != 0:
            data.extend(struct.pack('>Bi', 8, message.field1))

        if message.field2 != 0:
            data.extend(struct.pack('>Bi', 16, message.field2))

        if message.field3 != 0:
            data.extend(struct.pack('>Bi', 24, message.field3))

        return bytes(data)

    @staticmethod
    def decode(data):
        message = Lo_Field4()
        pos = 0

        while pos < len(data):
            field_number = struct.unpack('>B', data[pos:pos + 1])[0]
            pos += 1
            wire_type = field_number & 0x7
            field_number >>= 3

            if wire_type == 0:  # Varint
                if field_number == 1:
                    message.field1 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4
                elif field_number == 2:
                    message.field2 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4
                elif field_number == 3:
                    message.field3 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4

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
    def encode(message):
        data = bytearray()

        for value in message.field1:
            data.extend(struct.pack('>B', 10))
            data.extend(struct.pack('>I', len(value)))
            data.extend(value.encode('utf-8'))

        if len(message.field2) > 0:
            data.extend(struct.pack('>B', 18))
            data.extend(struct.pack('>I', len(message.field2)))
            data.extend(message.field2)

        if message.field3 != "":
            data.extend(struct.pack('>B', 26))
            data.extend(struct.pack('>I', len(message.field3)))
            data.extend(message.field3.encode('utf-8'))

        if message.field4 != 0:
            data.extend(struct.pack('>Bi', 32, message.field4))

        if message.field5 != 0:
            data.extend(struct.pack('>Bi', 40, message.field5))

        if message.field6 != "":
            data.extend(struct.pack('>B', 50))
            data.extend(struct.pack('>I', len(message.field6)))
            data.extend(message.field6.encode('utf-8'))

        return bytes(data)

    @staticmethod
    def decode(data):
        message = OQa()
        pos = 0

        while pos < len(data):
            field_number, wire_type = struct.unpack('>BB', data[pos:pos + 2])
            pos += 2

            if wire_type == 2:  # Length-delimited
                length = struct.unpack('>I', data[pos:pos + 4])[0]
                pos += 4
                field_data = data[pos:pos + length]
                pos += length

                if field_number == 1:
                    message.field1.append(field_data.decode('utf-8'))
                elif field_number == 2:
                    message.field2 = field_data
                elif field_number == 3:
                    message.field3 = field_data.decode('utf-8')
                elif field_number == 6:
                    message.field6 = field_data.decode('utf-8')

            elif wire_type == 0:  # Varint
                if field_number == 4:
                    message.field4 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4
                elif field_number == 5:
                    message.field5 = struct.unpack('>i', data[pos:pos + 4])[0]
                    pos += 4

        return message


class Pqa:
    def __init__(self):
        self.formats: List[FormatId] = []
        self.ud: List[BufferedRange] = []
        self.clip_id: str = ""

    @staticmethod
    def encode(message):
        data = bytearray()

        for format_id in message.formats:
            data.extend(struct.pack('>B', 10))
            format_id_data = FormatId.encode(format_id)
            data.extend(struct.pack('>I', len(format_id_data)))
            data.extend(format_id_data)

        for buffered_range in message.ud:
            data.extend(struct.pack('>B', 18))
            buffered_range_data = BufferedRange.encode(buffered_range)
            data.extend(struct.pack('>I', len(buffered_range_data)))
            data.extend(buffered_range_data)

        if message.clip_id != "":
            data.extend(struct.pack('>B', 26))
            data.extend(struct.pack('>I', len(message.clip_id)))
            data.extend(message.clip_id.encode('utf-8'))

        return bytes(data)

    @staticmethod
    def decode(data):
        message = Pqa()
        pos = 0

        while pos < len(data):
            field_number, wire_type = struct.unpack('>BB', data[pos:pos + 2])
            pos += 2

            if wire_type == 2:  # Length-delimited
                length = struct.unpack('>I', data[pos:pos + 4])[0]
                pos += 4
                field_data = data[pos:pos + length]
                pos += length

                if field_number == 1:
                    message.formats.append(FormatId.decode(field_data))
                elif field_number == 2:
                    message.ud.append(BufferedRange.decode(field_data))
                elif field_number == 3:
                    message.clip_id = field_data.decode('utf-8')

        return message