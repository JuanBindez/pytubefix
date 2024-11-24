"""
This module contains a container for stream manifest data.

A container object for the media stream (video only / audio only / video+audio
combined). This was referred to as ``Video`` in the legacy pytube version, but
has been renamed to accommodate DASH (which serves the audio and video
separately).
"""

import logging
import os
from math import ceil
import sys
import warnings

from datetime import datetime
from typing import BinaryIO, Dict, Optional, Tuple, Iterator, Callable
from urllib.error import HTTPError
from urllib.parse import parse_qs
from pathlib import Path

from pytubefix import extract, request
from pytubefix.helpers import safe_filename, target_directory
from pytubefix.itags import get_format_profile
from pytubefix.monostate import Monostate
from pytubefix.file_system import file_system_verify

logger = logging.getLogger(__name__)


class Stream:
    """Container for stream manifest data."""

    def __init__(
        self, stream: Dict, monostate: Monostate
    ):
        """Construct a :class:`Stream <Stream>`.

        :param dict stream:
            The unscrambled data extracted from YouTube.
        :param dict monostate:
            Dictionary of data shared across all instances of
            :class:`Stream <Stream>`.
        """
        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self._monostate = monostate

        self.url = stream["url"]  # signed download url
        self.itag = int(
            stream["itag"]
        )  # stream format id (youtube nomenclature)

        # set type and codec info

        # 'video/webm; codecs="vp8, vorbis"' -> 'video/webm', ['vp8', 'vorbis']
        self.mime_type, self.codecs = extract.mime_type_codec(stream["mimeType"])

        # 'video/webm' -> 'video', 'webm'
        self.type, self.subtype = self.mime_type.split("/")

        # ['vp8', 'vorbis'] -> video_codec: vp8, audio_codec: vorbis. DASH
        # streams return NoneType for audio/video depending.
        self.video_codec, self.audio_codec = self.parse_codecs()

        self.is_otf: bool = stream["is_otf"]
        self.bitrate: Optional[int] = stream["bitrate"]

        # filesize in bytes
        self._filesize: Optional[int] = int(stream.get('contentLength', 0))
        
        # filesize in kilobytes
        self._filesize_kb: Optional[float] = float(ceil(float(stream.get('contentLength', 0)) / 1024 * 1000) / 1000)
        
        # filesize in megabytes
        self._filesize_mb: Optional[float] = float(ceil(float(stream.get('contentLength', 0)) / 1024 / 1024 * 1000) / 1000)
        
        # filesize in gigabytes(fingers crossed we don't need terabytes going forward though)
        self._filesize_gb: Optional[float] = float(ceil(float(stream.get('contentLength', 0)) / 1024 / 1024 / 1024 * 1000) / 1000)

        # Additional information about the stream format, such as resolution,
        # frame rate, and whether the stream is live (HLS) or 3D.
        itag_profile = get_format_profile(self.itag)
        self.is_dash = itag_profile["is_dash"]
        self.abr = itag_profile["abr"]  # average bitrate (audio streams only)
        if 'fps' in stream:
            self.fps = stream['fps']  # Video streams only
        self.resolution = itag_profile[
            "resolution"
        ]  # resolution (e.g.: "480p")

        self._width = stream["width"] if 'width' in stream else None
        self._height = stream["height"] if 'height' in stream else None

        self.is_3d = itag_profile["is_3d"]
        self.is_hdr = itag_profile["is_hdr"]
        self.is_live = itag_profile["is_live"]

        self.includes_multiple_audio_tracks: bool = 'audioTrack' in stream
        if self.includes_multiple_audio_tracks:
            self.is_default_audio_track = stream['audioTrack']['audioIsDefault']
            self.audio_track_name = str(stream['audioTrack']['displayName']).split(" ")[0]
        else:
            self.is_default_audio_track = self.includes_audio_track and not self.includes_video_track
            self.audio_track_name = None

    @property
    def is_adaptive(self) -> bool:
        """Whether the stream is DASH.

        :rtype: bool
        """
        # if codecs has two elements (e.g.: ['vp8', 'vorbis']): 2 % 2 = 0
        # if codecs has one element (e.g.: ['vp8']) 1 % 2 = 1
        return bool(len(self.codecs) % 2)

    @property
    def is_progressive(self) -> bool:
        """Whether the stream is progressive.

        :rtype: bool
        """
        return not self.is_adaptive

    @property
    def includes_audio_track(self) -> bool:
        """Whether the stream only contains audio.

        :rtype: bool
        """
        return self.is_progressive or self.type == "audio"

    @property
    def includes_video_track(self) -> bool:
        """Whether the stream only contains video.

        :rtype: bool
        """
        return self.is_progressive or self.type == "video"

    def parse_codecs(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the video/audio codecs from list of codecs.

        Parse a variable length sized list of codecs and returns a
        constant two element tuple, with the video codec as the first element
        and audio as the second. Returns None if one is not available
        (adaptive only).

        :rtype: tuple
        :returns:
            A two element tuple with audio and video codecs.

        """
        video = None
        audio = None
        if not self.is_adaptive:
            video, audio = self.codecs
        elif self.includes_video_track:
            video = self.codecs[0]
        elif self.includes_audio_track:
            audio = self.codecs[0]
        return video, audio

    @property
    def width(self) -> int:
        """Video width. Returns None if it does not have the value.

        :rtype: int
        :returns:
            Returns an int of the video width
        """
        return self._width

    @property
    def height(self) -> int:
        """Video height. Returns None if it does not have the value.

        :rtype: int
        :returns:
            Returns an int of the video height
        """
        return self._height

    @property
    def filesize(self) -> int:
        """File size of the media stream in bytes.

        :rtype: int
        :returns:
            Filesize (in bytes) of the stream.
        """
        if self._filesize == 0:
            try:
                self._filesize = request.filesize(self.url)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize = request.seq_filesize(self.url)
        return self._filesize
    
    @property
    def filesize_kb(self) -> float:
        """File size of the media stream in kilobytes.

        :rtype: float
        :returns:
            Rounded filesize (in kilobytes) of the stream.
        """
        if self._filesize_kb == 0:
            try:
                self._filesize_kb = float(ceil(request.filesize(self.url)/1024 * 1000) / 1000)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize_kb = float(ceil(request.seq_filesize(self.url)/1024 * 1000) / 1000)
        return self._filesize_kb
    
    @property
    def filesize_mb(self) -> float:
        """File size of the media stream in megabytes.

        :rtype: float
        :returns:
            Rounded filesize (in megabytes) of the stream.
        """
        if self._filesize_mb == 0:
            try:
                self._filesize_mb = float(ceil(request.filesize(self.url)/1024/1024 * 1000) / 1000)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize_mb = float(ceil(request.seq_filesize(self.url)/1024/1024 * 1000) / 1000)
        return self._filesize_mb

    @property
    def filesize_gb(self) -> float:
        """File size of the media stream in gigabytes.

        :rtype: float
        :returns:
            Rounded filesize (in gigabytes) of the stream.
        """
        if self._filesize_gb == 0:
            try:
                self._filesize_gb = float(ceil(request.filesize(self.url)/1024/1024/1024 * 1000) / 1000)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize_gb = float(ceil(request.seq_filesize(self.url)/1024/1024/1024 * 1000) / 1000)
        return self._filesize_gb
    
    @property
    def title(self,) -> str:
        """Get title of video

        :rtype: str
        :returns:
            Youtube video title
        """
        return self._monostate.title or "Unknown YouTube Video Title"

    @property
    def filesize_approx(self) -> int:
        """Get approximate filesize of the video

        Falls back to HTTP call if there is not sufficient information to approximate

        :rtype: int
        :returns: size of video in bytes
        """
        if self._monostate.duration and self.bitrate:
            bits_in_byte = 8
            return int(
                (self._monostate.duration * self.bitrate) / bits_in_byte
            )

        return self.filesize

    @property
    def expiration(self) -> datetime:
        expire = parse_qs(self.url.split("?")[1])["expire"][0]
        return datetime.utcfromtimestamp(int(expire))

    @property
    def default_filename(self) -> str:
        """Generate filename based on the video title.

        :rtype: str
        :returns:
            An os file system compatible filename.
        """
        if 'audio' in self.mime_type and 'video' not in self.mime_type:
            self.subtype = "m4a"
        
        return f"{self.title}.{self.subtype}"

    def download(
        self,
        output_path: Optional[str] = None,
        filename: Optional[str] = None,
        filename_prefix: Optional[str] = None,
        skip_existing: bool = True,
        timeout: Optional[int] = None,
        max_retries: int = 0,
        interrupt_checker: Optional[Callable[[], bool]] = None
    ) -> Optional[str]:
        
        """
        Downloads a file from the URL provided by `self.url` and saves it locally with optional configurations.

        Args:
            output_path (Optional[str]): Directory path where the downloaded file will be saved. Defaults to the current directory if not specified.
            filename (Optional[str]): Custom name for the downloaded file. If not provided, a default name is used.
            filename_prefix (Optional[str]): Prefix to be added to the filename (if provided).
            skip_existing (bool): Whether to skip the download if the file already exists at the target location. Defaults to True.
            timeout (Optional[int]): Maximum time, in seconds, to wait for the download request. Defaults to None for no timeout.
            max_retries (int): The number of times to retry the download if it fails. Defaults to 0 (no retries).
            interrupt_checker (Optional[Callable[[], bool]]): A callable function that is checked periodically during the download. If it returns True, the download will stop without errors.

        Returns:
            Optional[str]: The full file path of the downloaded file, or None if the download was skipped or failed.

        Raises:
            HTTPError: Raised if there is an error with the HTTP request during the download process.

        Note:
            - The `skip_existing` flag avoids redownloading if the file already exists in the target location.
            - The `interrupt_checker` allows for the download to be halted cleanly if certain conditions are met during the download process.
            - Download progress can be monitored using the `on_progress` callback, and the `on_complete` callback is triggered once the download is finished.
        """
   
        kernel = sys.platform

        if kernel == "linux":
            file_system = "ext4"
        elif kernel == "darwin":
            file_system = "APFS"
        else:
            file_system = "NTFS"  
                
        translation_table = file_system_verify(file_system)

        if filename is None:
            filename = self.default_filename.translate(translation_table)

        if filename:
            filename = filename.translate(translation_table)

        file_path = self.get_file_path(
            filename=filename,
            output_path=output_path,
            filename_prefix=filename_prefix,
            file_system=file_system
        )

        if skip_existing and self.exists_at_path(file_path):
            logger.debug(f'file {file_path} already exists, skipping')
            self.on_complete(file_path)
            return file_path

        bytes_remaining = self.filesize
        logger.debug(f'downloading ({self.filesize} total bytes) file to {file_path}')

        with open(file_path, "wb") as fh:
            try:
                for chunk in request.stream(
                    self.url,
                    timeout=timeout,
                    max_retries=max_retries
                ):
                    if interrupt_checker is not None and interrupt_checker() == True:
                        logger.debug('interrupt_checker returned True, causing to force stop the downloading')
                        return
                    # reduce the (bytes) remainder by the length of the chunk.
                    bytes_remaining -= len(chunk)
                    # send to the on_progress callback.
                    self.on_progress(chunk, fh, bytes_remaining)
            except HTTPError as e:
                if e.code != 404:
                    raise
            except StopIteration:
                # Some adaptive streams need to be requested with sequence numbers
                for chunk in request.seq_stream(
                    self.url,
                    timeout=timeout,
                    max_retries=max_retries
                ):
                    if interrupt_checker is not None and interrupt_checker() == True:
                        logger.debug('interrupt_checker returned True, causing to force stop the downloading')
                        return
                    # reduce the (bytes) remainder by the length of the chunk.
                    bytes_remaining -= len(chunk)
                    # send to the on_progress callback.
                    self.on_progress(chunk, fh, bytes_remaining)

        self.on_complete(file_path)
        return file_path

    def get_file_path(
        self,
        filename: Optional[str] = None,
        output_path: Optional[str] = None,
        filename_prefix: Optional[str] = None,
        file_system: str = 'NTFS'
    ) -> str:
        if not filename:
            translation_table = file_system_verify(file_system)
            filename = self.default_filename.translate(translation_table)

        if filename:
            translation_table = file_system_verify(file_system)

            if not ('audio' in self.mime_type and 'video' not in self.mime_type):
                filename = filename.translate(translation_table)
            else:
                filename = filename.translate(translation_table)

        if filename_prefix:
            filename = f"{filename_prefix}{filename}"
        return str(Path(target_directory(output_path)) / filename)

    def exists_at_path(self, file_path: str) -> bool:
        return (
            os.path.isfile(file_path)
            and os.path.getsize(file_path) == self.filesize
        )

    def stream_to_buffer(self, buffer: BinaryIO) -> None:
        """Write the media stream to buffer

        :rtype: io.BytesIO buffer
        """
        bytes_remaining = self.filesize
        logger.info(
            "downloading (%s total bytes) file to buffer", self.filesize,
        )

        for chunk in request.stream(self.url):
            # reduce the (bytes) remainder by the length of the chunk.
            bytes_remaining -= len(chunk)
            # send to the on_progress callback.
            self.on_progress(chunk, buffer, bytes_remaining)
        self.on_complete(None)

    def on_progress(
        self, chunk: bytes, file_handler: BinaryIO, bytes_remaining: int
    ):
        """On progress callback function.

        This function writes the binary data to the file, then checks if an
        additional callback is defined in the monostate. This is exposed to
        allow things like displaying a progress bar.

        :param bytes chunk:
            Segment of media file binary data, not yet written to disk.
        :param file_handler:
            The file handle where the media is being written to.
        :type file_handler:
            :py:class:`io.BufferedWriter`
        :param int bytes_remaining:
            The delta between the total file size in bytes and amount already
            downloaded.

        :rtype: None

        """

        file_handler.write(chunk)

        logger.debug("download remaining: %s", bytes_remaining)
        if self._monostate.on_progress:
            self._monostate.on_progress(self, chunk, bytes_remaining)

    def on_complete(self, file_path: Optional[str]):
        """On download complete handler function.

        :param file_path:
            The file handle where the media is being written to.
        :type file_path: str

        :rtype: None

        """
        logger.debug("download finished")
        on_complete = self._monostate.on_complete
        if on_complete:
            logger.debug("calling on_complete callback %s", on_complete)
            on_complete(self, file_path)

    def __repr__(self) -> str:
        """Printable object representation.

        :rtype: str
        :returns:
            A string representation of a :class:`Stream <Stream>` object.
        """
        parts = ['itag="{s.itag}"', 'mime_type="{s.mime_type}"']
        if self.includes_video_track:
            parts.extend(['res="{s.resolution}"', 'fps="{s.fps}fps"'])
            if not self.is_adaptive:
                parts.extend(
                    ['vcodec="{s.video_codec}"', 'acodec="{s.audio_codec}"',]
                )
            else:
                parts.extend(['vcodec="{s.video_codec}"'])
        else:
            parts.extend(['abr="{s.abr}"', 'acodec="{s.audio_codec}"'])
        parts.extend(['progressive="{s.is_progressive}"', 'type="{s.type}"'])
        return f"<Stream: {' '.join(parts).format(s=self)}>"

    def on_progress_for_chunks(self, chunk: bytes, bytes_remaining: int):
        """On progress callback function.

        This function checks if an additional callback is defined in the monostate.
        This is exposed to allow things like displaying a progress bar.

        :param bytes chunk:
        Segment of media file binary data, not yet written to disk.
        :py:class:`io.BufferedWriter`
        :param int bytes_remaining:
        The delta between the total file size in bytes and amount already
        downloaded.

        :rtype: None
        """

        logger.debug("download remaining: %s", bytes_remaining)
        if self._monostate.on_progress:
            self._monostate.on_progress(self, chunk, bytes_remaining)

    def iter_chunks(self, chunk_size: Optional[int] = None) -> Iterator[bytes]:
        """Get the chunks directly

        Example:
        # Write the chunk by yourself
        with open("somefile.mp4") as out_file:
            out_file.writelines(stream.iter_chunks(512))

            # Another way
            # for chunk in stream.iter_chunks(512):
            #   out_file.write(chunk)

        # Or give it external api
        external_api.write_media(stream.iter_chunks(512))

        :param int chunk size:
        The size in the bytes
        :rtype: Iterator[bytes]
        """

        bytes_remaining = self.filesize

        if chunk_size:
            request.default_range_size = chunk_size

        logger.info(
            "downloading (%s total bytes) file to buffer",
            self.filesize,
        )
        try:
            stream = request.stream(self.url)
        except HTTPError as e:
            if e.code != 404:
                raise
            stream = request.seq_stream(self.url)

        for chunk in stream:
            bytes_remaining -= len(chunk)
            self.on_progress_for_chunks(chunk, bytes_remaining)
            yield chunk

        self.on_complete(None)
