# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryWriter, BinaryReader
from pytubefix.sabr.video_streaming.playback_cookie import PlaybackCookie


class NextRequestPolicy:
    def __init__(self):
        self.targetAudioReadaheadMs = 0
        self.targetVideoReadaheadMs = 0
        self.backoffTimeMs = 0
        self.playbackCookie = None
        self.videoId = ""

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("targetAudioReadaheadMs", 0) != 0:
            writer.uint32(8).int32(message["targetAudioReadaheadMs"])

        if message.get("targetVideoReadaheadMs", 0) != 0:
            writer.uint32(16).int32(message["targetVideoReadaheadMs"])

        if message.get("backoffTimeMs", 0) != 0:
            writer.uint32(32).int32(message["backoffTimeMs"])

        if message.get("playbackCookie") is not None:
            PlaybackCookie.encode(message["playbackCookie"], writer.uint32(58).fork()).join()

        if message.get("videoId", "") != "":
            writer.uint32(66).string(message["videoId"])

        return writer

    @staticmethod
    def decode(data, length=None):
        reader = data if isinstance(data, BinaryReader) else BinaryReader(data)
        end = reader.len if length is None else reader.pos + length
        message = NextRequestPolicy

        while reader.pos < end:
            tag = reader.uint32()
            field = tag >> 3

            if field == 1 and tag == 8:
                message.targetAudioReadaheadMs = reader.int32()
                continue
            elif field == 2 and tag == 16:
                message.targetVideoReadaheadMs = reader.int32()
                continue
            elif field == 4 and tag == 32:
                message.backoffTimeMs = reader.int32()
                continue
            elif field == 7 and tag == 58:
                message.playbackCookie = PlaybackCookie.decode(reader, reader.uint32())
                continue
            elif field == 8 and tag == 66:
                message.videoId = reader.string()
                continue
            elif (tag & 7) == 4 or tag == 0:
                break
            else:
                reader.skip(tag & 7)

        return message
