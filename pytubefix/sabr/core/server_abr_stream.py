# All credits to https://github.com/LuanRT/googlevideo

import enum
import base64
import logging
from enum import Enum
from time import sleep
from typing import Optional
from collections.abc import Callable
from urllib.request import Request, urlopen

from pytubefix.sabr.core.UMP import UMP
from pytubefix.monostate import Monostate
from pytubefix.exceptions import SABRError
from pytubefix.sabr.video_streaming.sabr_error import SabrError
from pytubefix.sabr.video_streaming.media_header import MediaHeader
from pytubefix.sabr.core.chunked_data_buffer import ChunkedDataBuffer
from pytubefix.sabr.video_streaming.sabr_redirect import SabrRedirect
from pytubefix.sabr.video_streaming.playback_cookie import PlaybackCookie
from pytubefix.sabr.video_streaming.next_request_policy import NextRequestPolicy
from pytubefix.sabr.video_streaming.streamer_context import StreamerContextUpdate
from pytubefix.sabr.video_streaming.stream_protection_status import StreamProtectionStatus
from pytubefix.sabr.video_streaming.video_playback_abr_request import VideoPlaybackAbrRequest
from pytubefix.sabr.video_streaming.format_initialization_metadata import FormatInitializationMetadata

logger = logging.getLogger(__name__)


# https://github.com/davidzeng0/innertube/blob/main/googlevideo/ump.md
class PART(Enum):
    ONESIE_HEADER = 10
    ONESIE_DATA = 11
    MEDIA_HEADER = 20
    MEDIA = 21
    MEDIA_END = 22
    LIVE_METADATA = 31
    HOSTNAME_CHANGE_HINT = 32
    LIVE_METADATA_PROMISE = 33
    LIVE_METADATA_PROMISE_CANCELLATION = 34
    NEXT_REQUEST_POLICY = 35
    USTREAMER_VIDEO_AND_FORMAT_DATA = 36
    FORMAT_SELECTION_CONFIG = 37
    USTREAMER_SELECTED_MEDIA_STREAM = 38
    FORMAT_INITIALIZATION_METADATA = 42
    SABR_REDIRECT = 43
    SABR_ERROR = 44
    SABR_SEEK = 45
    RELOAD_PLAYER_RESPONSE = 46
    PLAYBACK_START_POLICY = 47
    ALLOWED_CACHED_FORMATS = 48
    START_BW_SAMPLING_HINT = 49
    PAUSE_BW_SAMPLING_HINT = 50
    SELECTABLE_FORMATS = 51
    REQUEST_IDENTIFIER = 52
    REQUEST_CANCELLATION_POLICY = 53
    ONESIE_PREFETCH_REJECTION = 54
    TIMELINE_CONTEXT = 55
    REQUEST_PIPELINING = 56
    SABR_CONTEXT_UPDATE = 57
    STREAM_PROTECTION_STATUS = 58
    SABR_CONTEXT_SENDING_POLICY = 59
    LAWNMOWER_POLICY = 60
    SABR_ACK = 61
    END_OF_TRACK = 62
    CACHE_LOAD_POLICY = 63
    LAWNMOWER_MESSAGING_POLICY = 64
    PREWARM_CONNECTION = 65
    PLAYBACK_DEBUG_INFO = 66
    SNACKBAR_MESSAGE = 67


# Reference https://github.com/coletdjnz/yt-dlp-dev/blob/5c0c2963396009a92101bc6e038b61844368409d/yt_dlp/extractor/youtube/_streaming/sabr/part.py
class PoTokenStatus(enum.Enum):
    UNKNOWN = -1
    OK = enum.auto()               # PO Token is provided and valid
    MISSING = enum.auto()          # PO Token is not provided, and is required. A PO Token should be provided ASAP
    INVALID = enum.auto()          # PO Token is provided, but is invalid. A new one should be generated ASAP
    PENDING = enum.auto()          # PO Token is provided, but probably only a cold start token. A full PO Token should be provided ASAP
    NOT_REQUIRED = enum.auto()     # PO Token is not provided, and is not required
    PENDING_MISSING = enum.auto()  # PO Token is not provided, but is pending. A full PO Token should be (probably) provided ASAP


class ServerAbrStream:
    def __init__(self, stream, write_chunk: Callable, monostate: Monostate):

        self.stream = stream
        self.write_chunk = write_chunk
        self.youtube = monostate.youtube
        self.po_token = self.stream.po_token
        self.server_abr_streaming_url = self.stream.url
        self.video_playback_ustreamer_config = self.stream.video_playback_ustreamer_config
        self.totalDurationMs = int(self.stream.durationMs)
        self.bytes_remaining = self.stream.filesize
        self.initialized_formats = []
        self.formats_by_key = {}
        self.playback_cookie = None
        self.header_id_to_format_key_map = {}
        self.previous_sequences = {}
        self.RELOAD = False
        self.maximum_reload_attempt = 4
        self.stream_protection_status = PoTokenStatus.UNKNOWN.name
        self.sabr_contexts_to_send = []
        self.sabr_context_updates = dict()

    def emit(self, data):
        for formatId in data['initialized_formats']:
            if formatId['formatId']['itag'] == self.stream.itag:
                media_chunks = formatId['mediaChunks']
                for chunk in media_chunks:
                    self.bytes_remaining -= len(chunk)
                    self.write_chunk(chunk, self.bytes_remaining)

    def start(self):

        audio_format = [{'itag': self.stream.itag,
                         'lastModified': int(self.stream.last_Modified),
                         'xtags': self.stream.xtags}] if self.stream.type == 'audio' else []

        video_format = [{'itag': self.stream.itag,
                         'lastModified': int(self.stream.last_Modified),
                         'xtags': self.stream.xtags}] if self.stream.type == 'video' else []

        client_abr_state = {
            'lastManualDirection': 0,
            'timeSinceLastManualFormatSelectionMs': 0,
            'lastManualSelectedResolution': int(self.stream.resolution.replace('p', '')) if video_format else 720,
            'stickyResolution': int(self.stream.resolution.replace('p', '')) if video_format else 720,
            'playerTimeMs': 0,
            'visibility': 0,
            'drcEnabled': self.stream.is_drc,
            # 0 = BOTH, 1 = AUDIO (video-only is no longer supported by YouTube)
            'enabledTrackTypesBitfield': 0 if video_format else 1
        }
        while client_abr_state['playerTimeMs'] < self.totalDurationMs:
            data = self.fetch_media(client_abr_state, audio_format, video_format)

            if data.get("sabr_error"):
                logger.debug("SABR error type: %s", data["sabr_error"].type)
                self.reload()

            self.emit(data)

            if data.get("sabr_context_update"):
                if self.maximum_reload_attempt > 0:
                    continue
                else:
                    raise SABRError("SABR failed to update context after exhausting reload attempts")

            # Determine main format
            if client_abr_state["enabledTrackTypesBitfield"] == 0:
                main_format = next(
                    (fmt for fmt in data.get("initialized_formats", []) if "video" in (fmt.get("mimeType") or "")),
                    None
                )
            else:
                main_format = data['initialized_formats'][0] if data['initialized_formats'] else None

            # Register sequence numbers
            for fmt in data.get("initialized_formats", []):
                format_key = fmt["formatKey"]
                sequence_numbers = [seq.get("sequenceNumber", 0) for seq in fmt.get("sequenceList", [])]
                self.previous_sequences[format_key] = sequence_numbers

            # Check if server returned usable chunks
            if not self.RELOAD and (
                    main_format is None or
                    not main_format.get("sequenceList")
            ):
                logger.debug("SABR No chunks returned by the ABR server, triggering reload")
                self.reload()

            # Handle reload attempts
            if self.RELOAD:
                if self.maximum_reload_attempt > 0:
                    self.RELOAD = False
                    continue
                else:
                    raise SABRError(
                        f"SABR Maximum reload attempts reached. Stream protection status: PoToken {self.stream_protection_status}"
                    )

            # Check for end of media
            if (
                    not main_format or
                    main_format["sequenceCount"] == main_format["sequenceList"][-1].get("sequenceNumber")
            ):
                break

            # Update client player time
            total_sequence_duration = sum(seq.get("durationMs", 0) for seq in main_format["sequenceList"])
            client_abr_state["playerTimeMs"] += total_sequence_duration

    def fetch_media(self, client_abr_state, audio_format, video_format):
        body = VideoPlaybackAbrRequest.encode({
            'clientAbrState': client_abr_state,
            'selectedAudioFormatIds': audio_format,
            'selectedVideoFormatIds': video_format,
            'selectedFormatIds': [fmt["formatId"] for fmt in self.initialized_formats],
            'videoPlaybackUstreamerConfig': self.base64_to_u8(self.video_playback_ustreamer_config),
            'streamerContext': {
                'sabrContexts': [
                    ctx
                    for ctx in self.sabr_context_updates.values() if ctx["type"] in self.sabr_contexts_to_send
                ],
                'field6': [],
                'poToken': self.base64_to_u8(self.po_token) if self.po_token else None,
                'playbackCookie': PlaybackCookie.encode(
                    self.playback_cookie).finish() if self.playback_cookie else None,
                'clientInfo': {
                    'clientName': 1,
                    'clientVersion': '2.20250523.01.00',
                    'osName': 'Windows',
                    'osVersion': '10.0',
                    'platform': 'DESKTOP'
                }
            },
            'bufferedRanges': [fmt["_state"] for fmt in self.initialized_formats],
            'field1000': []
        }).finish()

        base_headers = {
            "User-Agent": "Mozilla/5.0", "accept-language": "en-US,en", "Content-Type": "application/vnd.yt-ump",
        }
        request = Request(self.server_abr_streaming_url, headers=base_headers, method="POST", data=bytes(body))
        return self.parse_ump_response(bytes(urlopen(request).read()))

    def parse_ump_response(self, response):
        self.header_id_to_format_key_map.clear()
        for k, v in enumerate(self.initialized_formats):
            self.initialized_formats[k]['sequenceList'] = []
            self.initialized_formats[k]['mediaChunks'] = []

        sabr_error: Optional[SabrError] = None
        sabr_redirect: Optional[SabrRedirect] = None
        sabr_context_update: bool = False

        ump = UMP(ChunkedDataBuffer([response]))

        def callback(part):
            data = list(part['data'].chunks[0] if part['data'].chunks else [])

            if part['type'] == PART.MEDIA_HEADER.value:
                self.process_media_header(data)

            elif part['type'] == PART.MEDIA.value:
                self.process_media_data(part['data'])

            elif part['type'] == PART.MEDIA_END.value:
                self.process_end_of_media(part['data'])

            elif part['type'] == PART.NEXT_REQUEST_POLICY.value:
                self.process_next_request_policy(data)

            elif part['type'] == PART.FORMAT_INITIALIZATION_METADATA.value:
                self.process_format_initialization(data)

            elif part['type'] == PART.SABR_ERROR.value:
                nonlocal sabr_error
                sabr_error = SabrError.decode(data)

            elif part['type'] == PART.SABR_REDIRECT.value:
                nonlocal sabr_redirect
                sabr_redirect = self.process_sabr_redirect(data)
                logger.debug("SABR_REDIRECT")

            elif part['type'] == PART.STREAM_PROTECTION_STATUS.value:
                self.process_stream_protection_status(data)

            elif part['type'] == PART.RELOAD_PLAYER_RESPONSE.value:
                logger.debug("RELOAD_PLAYER_RESPONSE")
                self.reload()

            elif part["type"] == PART.PLAYBACK_START_POLICY.value:
                pass

            elif part["type"] == PART.REQUEST_CANCELLATION_POLICY.value:
                pass

            elif part["type"] == PART.SABR_CONTEXT_UPDATE.value:  # YouTube tries to force ads to appear
                nonlocal sabr_context_update
                sabr_context_update = True
                self.process_sabr_context_update(data)

            elif part["type"] == PART.SNACKBAR_MESSAGE.value:  # This forces you to wait for the time to be able to skip the ad.
                sabr_context_update = True
                self.process_snackbar_message()

        ump.parse(callback)

        return {
            "initialized_formats": self.initialized_formats,
            "sabr_redirect": sabr_redirect,
            "sabr_error": sabr_error,
            "sabr_context_update": sabr_context_update
        }

    def process_media_header(self, data):
        media_header = MediaHeader.decode(data)

        if not media_header.formatId:
            return

        format_key = self.get_format_key(media_header.formatId)
        current_format = self.formats_by_key.get(format_key) or self.register_format(media_header)

        if not current_format:
            return

        sequence_number = media_header.sequenceNumber
        if sequence_number is not None:
            if format_key in self.previous_sequences:
                if sequence_number in self.previous_sequences[format_key]:
                    return

        header_id = media_header.headerId
        if header_id is not None:
            if header_id not in self.header_id_to_format_key_map:
                self.header_id_to_format_key_map[header_id] = format_key

        if not any(seq.get("sequenceNumber") == (media_header.sequenceNumber or 0) for seq in
                   current_format["sequenceList"]):
            current_format["sequenceList"].append({
                "itag": media_header.itag,
                "formatId": media_header.formatId,
                "isInitSegment": media_header.isInitSeg,
                "durationMs": media_header.durationMs,
                "startMs": media_header.startMs,
                "startDataRange": media_header.startRange,
                "sequenceNumber": media_header.sequenceNumber,
                "contentLength": media_header.contentLength,
                "timeRange": media_header.timeRange
            })

            if isinstance(sequence_number, int):
                current_format["_state"]["durationMs"] += media_header.durationMs
                current_format["_state"]["endSegmentIndex"] += 1

    def process_media_data(self, data):
        header_id = data.get_uint8(0)
        stream_data = data.split(1)['remaining_buffer']
        format_key = self.header_id_to_format_key_map.get(header_id)
        if not format_key:
            return

        current_format = self.formats_by_key.get(format_key)
        if not current_format:
            return

        current_format['mediaChunks'].append(stream_data.chunks[0])

    def process_end_of_media(self, data):
        header_id = data.get_uint8(0)
        self.header_id_to_format_key_map.pop(header_id, None)

    def process_next_request_policy(self, data):
        next_request_policy = NextRequestPolicy.decode(data)
        self.playback_cookie = next_request_policy.playbackCookie

    def process_format_initialization(self, data):
        format_metadata = FormatInitializationMetadata.decode(data)
        self.register_format(format_metadata)

    def process_sabr_redirect(self, data):
        sabr_redirect = SabrRedirect.decode(data)
        if not sabr_redirect.url:
            raise ValueError("Invalid SABR redirect")
        self.server_abr_streaming_url = sabr_redirect.url
        return sabr_redirect

    def process_snackbar_message(self):
        skip = self.sabr_context_updates[self.sabr_contexts_to_send[-1]].get("skip", 1000) / 1000

        if skip >= 60:
            raise SABRError("SABR The maximum time to skip the ad (1 minute) has been exceeded.")

        logger.warning(f"SABR YouTube is forcing ads, wait {skip} seconds to skip")

        sleep(skip)
        self.maximum_reload_attempt -= 1

    # Reference https://github.com/coletdjnz/yt-dlp-dev/blob/5c0c296/yt_dlp/extractor/youtube/_streaming/sabr/stream.py
    def process_stream_protection_status(self, data):
        protection_status = StreamProtectionStatus.decode(data).status

        if protection_status == StreamProtectionStatus.Status.OK.value:
            result_status = PoTokenStatus.OK.name if self.po_token else PoTokenStatus.NOT_REQUIRED.name

        elif protection_status == StreamProtectionStatus.Status.ATTESTATION_PENDING.value:
            result_status = PoTokenStatus.PENDING.name if self.po_token else PoTokenStatus.PENDING_MISSING.name

        elif protection_status == StreamProtectionStatus.Status.ATTESTATION_REQUIRED.value:
            result_status = PoTokenStatus.INVALID.name if self.po_token else PoTokenStatus.MISSING.name

        else:
            result_status = PoTokenStatus.UNKNOWN.name

        self.stream_protection_status = result_status

        logger.debug(f"Stream Protection Status: PoToken {self.stream_protection_status}")

    # Reference https://github.com/coletdjnz/yt-dlp-dev/blob/5c0c296/yt_dlp/extractor/youtube/_streaming/sabr/stream.py
    def process_sabr_context_update(self, data):
        sabr_ctx_update = StreamerContextUpdate.decode(data)

        if not (sabr_ctx_update["type"] and sabr_ctx_update["value"] and sabr_ctx_update["writePolicy"]):
            logger.debug('Received an invalid SabrContextUpdate, ignoring')
            return
        if (
                sabr_ctx_update[
                    "writePolicy"] == StreamerContextUpdate.SabrContextWritePolicy.SABR_CONTEXT_WRITE_POLICY_KEEP_EXISTING.value
                and sabr_ctx_update["type"] in self.sabr_context_updates
        ):
            logger.debug(
                'Received a SABR Context Update with writePolicy=KEEP_EXISTING'
                'matching an existing SABR Context Update. Ignoring update')
            return

        self.sabr_context_updates[sabr_ctx_update["type"]] = sabr_ctx_update

        timestamp = sabr_ctx_update.get("value", "").get("field1", "").get("timestamp", "")
        skip = sabr_ctx_update.get("value", "").get("field1", "").get("skip", "")

        self.sabr_context_updates[sabr_ctx_update["type"]]["timestamp"] = timestamp
        self.sabr_context_updates[sabr_ctx_update["type"]]["skip"] = skip

        if sabr_ctx_update["sendByDefault"] is True:
            self.sabr_contexts_to_send.append(sabr_ctx_update["type"])

        logger.debug(f'Registered SabrContextUpdate')
        logger.debug(f"Current timestamp: {timestamp}")
        logger.debug(f"Please wait for {skip} milliseconds")

    @staticmethod
    def get_format_key(format_id) -> str:
        return f"{format_id['itag']};{format_id['lastModified']};"

    def register_format(self, data):
        if data.formatId is None:
            return None

        format_key = self.get_format_key(data.formatId)

        if format_key not in self.formats_by_key:
            format_ = {
                "formatId": data.formatId,
                "formatKey": format_key,
                "durationMs": data.durationMs,
                "mimeType": data.mimeType,
                "sequenceCount": data.endSegmentNumber,
                "sequenceList": [],
                "mediaChunks": [],
                "_state": {
                    "formatId": data.formatId,
                    "startTimeMs": 0,
                    "durationMs": 0,
                    "startSegmentIndex": 1,
                    "endSegmentIndex": 0
                }
            }
            self.initialized_formats.append(format_)
            self.formats_by_key[format_key] = self.initialized_formats[-1]
            return format_
        return None

    def reload(self):
        logger.debug("Refreshing SABR streaming URL")

        self.RELOAD = True
        self.maximum_reload_attempt -= 1

        # ContextUpdate is bound to server url
        self.sabr_contexts_to_send = []
        self.sabr_context_updates = dict()

        self.youtube.vid_info = None
        refresh_url = self.youtube.server_abr_streaming_url
        if not refresh_url:
            raise ValueError("Invalid SABR refresh")
        self.server_abr_streaming_url = refresh_url
        self.video_playback_ustreamer_config = self.youtube.video_playback_ustreamer_config

    @staticmethod
    def base64_to_u8(base64_str):
        standard_base64 = base64_str.replace('-', '+').replace('_', '/')
        padded_base64 = standard_base64 + '=' * ((4 - len(standard_base64) % 4) % 4)
        byte_data = base64.b64decode(padded_base64)
        return bytearray(byte_data)
