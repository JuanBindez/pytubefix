"""Library specific exception definitions."""
from typing import Pattern, Union
from .colors import Color

c = Color()

class PytubeFixError(Exception):
    """Base pytube exception that all others inherit.

    This is done to not pollute the built-in exceptions, which *could* result
    in unintended errors being unexpectedly and incorrectly handled within
    implementers code.
    """

class MaxRetriesExceeded(PytubeFixError):
    """Maximum number of retries exceeded."""


class HTMLParseError(PytubeFixError):
    """HTML could not be parsed"""


class ExtractError(PytubeFixError):
    """Data extraction based exception."""


class RegexMatchError(ExtractError):
    """Regex pattern did not return any matches."""

    def __init__(self, caller: str, pattern: Union[str, Pattern]):
        """
        :param str caller:
            Calling function
        :param str pattern:
            Pattern that failed to match
        """
        super().__init__(f"{c.RED}{caller}: could not find match for {pattern}{c.RESET}")
        self.caller = caller
        self.pattern = pattern


class VideoUnavailable(PytubeFixError):
    """Base video unavailable error."""
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.error_string)

    @property
    def error_string(self):
        return f'{c.RED}{self.video_id} is unavailable{c.RESET}'


class AgeRestrictedError(VideoUnavailable):
    """Video is age restricted, and cannot be accessed without OAuth."""
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f"{c.RED}Video ID = {self.video_id}: is age restricted, and can't be accessed without logging in.{c.RESET}"


class LiveStreamError(VideoUnavailable):
    """Video is a live stream."""
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{c.RED}{self.video_id} is streaming live and cannot be loaded{c.RESET}'


class VideoPrivate(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{c.RED}{self.video_id} is a private video{c.RESET}'


class RecordingUnavailable(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{c.RED}{self.video_id} does not have a live stream recording available{c.RESET}'


class MembersOnly(VideoUnavailable):
    """Video is members-only.

    YouTube has special videos that are only viewable to users who have
    subscribed to a content creator.
    ref: https://support.google.com/youtube/answer/7544492?hl=en
    """
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{c.RED}{self.video_id} is a members-only video{c.RESET}'


class VideoRegionBlocked(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{c.RED}{self.video_id} is not available in your region{c.RESET}'
